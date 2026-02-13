"""
SITE FINDER DEMO SCRIPT
=======================

Purpose
-------
This script demonstrates how to use the Hermes Health Site Finder API to look up
healthcare facility records based on address data. It will:

1. Start a local webhook receiver on a configurable port
2. Submit one or more test cases to the `/v0/site-finder` endpoint with webhook_url
3. Print the initial response (found site, matches, nearby sites)
4. Wait for the background research webhook callback with enriched site data

The Site Finder endpoint finds or creates a facility, and automatically triggers
AI-powered background research if the site hasn't been researched recently. When
a webhook_url is provided, the enriched site data is POSTed to that URL once
research completes (typically 30-60 seconds).

Prerequisites
-------------
- Python 3.6+
- `requests` library (install via `pip install requests`)

Configuration
-------------
Edit the variables below:

    DOMAIN      = "https://api.hermeshealth.ai"  # Base API URL
    API_KEY     = "<YOUR_API_KEY>"               # Your Hermes Health API key
    WEBHOOK_PORT = 8777                          # Local port for webhook receiver
    WEBHOOK_HOST = "<YOUR_PUBLIC_URL>"           # Public URL that the API can reach

Usage
-----
    python site_research_demo.py

Since this is a demo, the test cases are hard-coded in the script. You can
replace `TEST_CASES` or adapt the code to read from a file or other source.

Output
------
For each test case, you'll see:

1. The initial site finder response (found site, match confidence, nearby sites)
2. A webhook callback with the fully researched site data (phone numbers, fax,
   email, ROI vendor info, etc.) once background research completes

"""

import requests
import json
import hmac
import hashlib
import uuid
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ---------------------
# Configuration
# ---------------------
DOMAIN = "https://api.hermeshealth.ai"
API_KEY = ""  # insert your API key here

# Webhook receiver settings
# WEBHOOK_HOST must be a URL reachable by the Hermes API server.
# For local development, you can use a tunnel service (e.g. ngrok) and set
# WEBHOOK_HOST to your tunnel URL. The local server always binds to 0.0.0.0.
WEBHOOK_PORT = 8777
WEBHOOK_HOST = "http://localhost:8777"  # e.g. "https://abc123.ngrok.io" — leave empty to skip webhooks

# Your company's webhook secret (UUID) from the Hermes Health dashboard.
# Used to verify HMAC-SHA256 signatures on incoming webhooks.
# Leave empty to skip signature verification.
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
    """Simple HTTP handler that receives POST callbacks from the Site Finder."""

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

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return

        site_name = payload.get("site", {}).get("siteName", "unknown")
        site_id = payload.get("site", {}).get("id", "?")

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
        # Silence default request logging
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
# Main
# ---------------------
if __name__ == "__main__":
    use_webhooks = bool(WEBHOOK_HOST)

    if use_webhooks:
        webhook_url_base = WEBHOOK_HOST.rstrip("/")
        print(f"Starting webhook receiver on port {WEBHOOK_PORT}...")
        print(f"Webhook URL base: {webhook_url_base}")
        server_thread = threading.Thread(target=start_webhook_server, daemon=True)
        server_thread.start()
    else:
        print("WEBHOOK_HOST not set — skipping webhook callbacks.")
        print("You will still see the initial site finder response.\n")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    max_eta = 0  # Track the longest research ETA across all responses

    for test_case in TEST_CASES:
        site_name = test_case["name"]

        print(f"\nLooking up: {site_name}")
        print("-" * 50)

        # Build request body — include webhook_url if configured
        body = dict(test_case)
        if use_webhooks:
            body["webhookUrl"] = f"{webhook_url_base}/site-research-callback"

        # Call the Site Finder endpoint
        response = requests.post(
            f"{DOMAIN}/v0/site-finder",
            headers=headers,
            json=body
        )

        print(f"Status: {response.status_code}")
        result = response.json()

        # Track research ETA and which site IDs to expect webhooks for
        eta = result.get("researchEta")
        if eta:
            max_eta = max(max_eta, eta)

        # Summarize the initial response
        found = result.get("foundSite")
        if found:
            site = found["site"]
            found_id = site.get("id")
            print(f"  Found: {site.get('siteName')} (id={found_id})")
            print(f"  Confidence: {found.get('confidenceScore')}%")
            print(f"  Distance: {found.get('distanceFeet')} ft")
            print(f"  Reason: {found.get('reason')}")
            if eta:
                pending_site_ids.add(found_id)
                print(f"  Background research triggered (ETA ~{eta}s)")
            else:
                researched = site.get("researchFinished")
                if researched:
                    print(f"  Last researched: {researched}")
        else:
            print("  No matching site found")

        matches = result.get("allMatches", [])
        if len(matches) > 1:
            print(f"  Additional matches: {len(matches) - 1}")

        nearby = result.get("nearbySites", [])
        print(f"  Nearby sites within radius: {len(nearby)}")

    if use_webhooks and pending_site_ids:
        print(f"\n{'=' * 60}")
        print(f"Waiting up to {max_eta}s for {len(pending_site_ids)} background research webhook(s)...")
        print(f"(expecting site IDs: {', '.join(str(s) for s in sorted(pending_site_ids))})")
        print("=" * 60)

        finished = all_done.wait(timeout=max_eta)
        if finished:
            print(f"\nAll {len(webhook_results)} webhook(s) received.")
        else:
            total = len(webhook_results) + len(pending_site_ids)
            print(f"\nTimed out after {max_eta}s. Received {len(webhook_results)}/{total} webhook(s).")
            if pending_site_ids:
                print(f"Still waiting on site IDs: {', '.join(str(s) for s in sorted(pending_site_ids))}")
    elif use_webhooks:
        print("\nNo background research triggered — no webhooks expected.")
        all_done.set()

    print("\nDone.")
