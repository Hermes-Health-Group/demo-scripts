"""
SITE FINDER DEMO SCRIPT
=======================

Demonstrates the Hermes Health Site Finder API. For each test case it:

1. Submits the address to /v0/site-finder
2. Prints the initial response (found site, matches, nearby sites)
3. Waits for enriched site data via polling (default) or webhook

Prerequisites: Python 3.6+, `pip install requests`

Usage:
    python site_research_demo.py              # polling mode (default)
    python site_research_demo.py --webhook    # webhook mode
"""

import argparse
import requests
import json
import time
import hmac
import hashlib
import uuid
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ---------------------
# Configuration
# ---------------------
DOMAIN = "https://api.hermeshealth.dev"
API_KEY = ""  # insert your API key here

# Webhook receiver settings
# For local development, use a tunnel service (e.g. ngrok) and set
# WEBHOOK_HOST to your tunnel URL.
WEBHOOK_PORT = 8777
WEBHOOK_HOST = "http://localhost:8777"  # e.g. "https://abc123.ngrok.io"

# Your company's webhook secret (UUID) from the Hermes Health dashboard.
# Used to verify HMAC-SHA256 signatures on incoming webhooks.
WEBHOOK_SECRET = ""  # e.g. "d1234567-abcd-1234-abcd-1234567890ab"

# Demo test cases
TEST_CASES = [
    {
        "name": "Ochsner Medical Center",
        "address": "1514 Jefferson Hwy",
        "city": "Jefferson",
        "state": "LA",
        "zip": "70121"
    },
    {
        "name": "Woman's Hospital",
        "address": "100 Woman's Way",
        "city": "Baton Rouge",
        "state": "LA",
        "zip": "70817"
    }
]

# ---------------------
# Webhook receiver
# ---------------------
webhook_results = {}  # site_id -> payload
pending_site_ids = set()  # site IDs we expect webhooks for
all_done = threading.Event()


def verify_webhook_signature(body: bytes, signature: str, secret: str) -> bool:
    """Verify the HMAC-SHA256 signature using the company's webhook secret (UUID).

    The secret UUID is converted to its 16-byte binary form (matching Rust's
    uuid.as_bytes()), then used as the HMAC key.
    """
    secret_bytes = uuid.UUID(secret).bytes
    expected = hmac.new(secret_bytes, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Verify HMAC signature if a webhook secret is configured
        if WEBHOOK_SECRET:
            signature = self.headers.get("X-Webhook-Signature", "")
            if not verify_webhook_signature(body, signature, WEBHOOK_SECRET):
                print("\nWARNING: Invalid webhook signature! Rejecting request.")
                self.send_response(401)
                self.end_headers()
                return
            print("  Signature verified.")

        payload = json.loads(body)
        site_name = payload["site"]["siteName"]
        site_id = payload["site"]["id"]

        print(f"\n{'=' * 60}")
        print(f"WEBHOOK RECEIVED — Research complete for: {site_name} (id={site_id})")
        print("=" * 60)
        print(json.dumps(payload, indent=2))

        webhook_results[site_id] = payload
        pending_site_ids.discard(site_id)
        if not pending_site_ids:
            all_done.set()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"received"}')

    def log_message(self, format, *args):
        pass


def start_webhook_server():
    server = HTTPServer(("0.0.0.0", WEBHOOK_PORT), WebhookHandler)
    server.timeout = 1
    # Run until the main thread signals completion or 5 minutes elapse
    while not all_done.wait(timeout=0.5):
        server.handle_request()
    # Drain any final request
    server.handle_request()
    server.server_close()


# ---------------------
# Polling
# ---------------------
def poll_for_research(site_id, site_name, headers, eta):
    """Poll GET /v0/sites/{id} until researchFinished is populated."""
    print(f"\n  Polling for research on: {site_name} (ETA ~{eta}s)")
    time.sleep(eta / 2)  # initial delay before polling
    while True:
        time.sleep(5)
        resp = requests.get(f"{DOMAIN}/v0/sites/{site_id}", headers=headers)
        site_data = resp.json()
        if site_data["site"].get("researchFinished"):
            print(f"\n{'=' * 60}")
            print(f"RESEARCH COMPLETE — {site_name} (id={site_id})")
            print("=" * 60)
            print(json.dumps(site_data, indent=2))
            return
        print(f"  ... still researching {site_name}")


# ---------------------
# Main
# ---------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Health Site Finder demo")
    parser.add_argument(
        "--webhook", action="store_true",
        help="Use webhook mode instead of polling (default: polling)"
    )
    args = parser.parse_args()

    use_webhook = args.webhook

    if use_webhook:
        webhook_url_base = WEBHOOK_HOST.rstrip("/")
        print(f"Starting webhook receiver on port {WEBHOOK_PORT}...")
        server_thread = threading.Thread(target=start_webhook_server, daemon=True)
        server_thread.start()

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    max_eta = 0
    poll_threads = []

    for test_case in TEST_CASES:
        site_name = test_case["name"]

        print(f"\nLooking up: {site_name}")
        print("-" * 50)

        body = dict(test_case)
        if use_webhook:
            body["webhookUrl"] = f"{webhook_url_base}/site-research-callback"

        response = requests.post(
            f"{DOMAIN}/v0/site-finder",
            headers=headers,
            json=body
        )

        print(f"Status: {response.status_code}")
        result = response.json()

        eta = result.get("researchEta")
        if eta:
            max_eta = max(max_eta, eta)

        found = result.get("foundSite")
        if found:
            site = found["site"]
            found_id = site["id"]
            print(f"  Found: {site['siteName']} (id={found_id})")
            print(f"  Confidence: {found['confidenceScore']}%")
            print(f"  Distance: {found['distanceFeet']} ft")
            print(f"  Reason: {found['reason']}")
            if eta:
                if use_webhook:
                    pending_site_ids.add(found_id)
                else:
                    t = threading.Thread(
                        target=poll_for_research,
                        args=(found_id, site['siteName'], headers, eta),
                        daemon=True
                    )
                    t.start()
                    poll_threads.append(t)
                print(f"  Background research triggered (ETA ~{eta}s)")
            else:
                print(f"  Last researched: {site.get('researchFinished')}")
        else:
            print("  No matching site found")

        matches = result.get("allMatches", [])
        if len(matches) > 1:
            print(f"  Additional matches: {len(matches) - 1}")

        nearby = result.get("nearbySites", [])
        print(f"  Nearby sites within radius: {len(nearby)}")

    # Wait for research results
    if use_webhook and pending_site_ids:
        print(f"\n{'=' * 60}")
        print(f"Waiting for {len(pending_site_ids)} background research webhook(s)...")
        print("=" * 60)
        all_done.wait()
        print(f"\nReceived {len(webhook_results)} webhook(s).")
    elif poll_threads:
        for t in poll_threads:
            t.join()
    else:
        all_done.set()

    print("\nDone.")
