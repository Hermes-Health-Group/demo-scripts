# Hermes Health Webhook Receiver Demo Script
# --------------------------------------------
# This script demonstrates how to:
# 1. Receive webhook notifications from Hermes Health when a record request status changes
# 2. Validate the HMAC-SHA256 signature to ensure the webhook is authentic
# 3. Process the webhook payload (record request data)
#
# Install dependencies:
# pip install flask
#
# Run with:
# python webhook_receiver_demo.py
#
# The server will start on port 5000, you will need to configure DNS to point to this server
# Configure this the webhook URL in your Hermes Health company settings

from flask import Flask, request, jsonify
import hmac
import hashlib
import json
import uuid

# --------------------
# Configuration values
# --------------------
WEBHOOK_SECRET = ""  # Replace with your webhook secret from settings

# ------------------------
# Flask app setup
# ------------------------
app = Flask(__name__)

def verify_webhook_signature(payload_body, signature_header, secret):
    """
    Verify that the webhook request came from Hermes Health by validating
    the HMAC-SHA256 signature.
    
    Args:
        payload_body: Raw request body as bytes
        signature_header: The X-Webhook-Signature header value
        secret: Your webhook secret (UUID as string)
    
    Returns:
        True if signature is valid, False otherwise
    """
    # Parse the UUID string and convert to bytes (16-byte binary representation)
    # This matches how Rust's uuid.as_bytes() works
    secret_uuid = uuid.UUID(secret)
    secret_bytes = secret_uuid.bytes
    
    # Compute HMAC-SHA256 of the payload
    computed_hmac = hmac.new(
        secret_bytes,
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures (constant-time comparison to prevent timing attacks)
    return hmac.compare_digest(computed_hmac, signature_header)

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint that receives record request status updates from Hermes Health.
    """
    print("\n" + "="*60)
    print("Received webhook from Hermes Health")
    print("="*60)
    
    # Get the signature from headers
    signature = request.headers.get('X-Webhook-Signature')
    
    # Get raw request body for signature verification
    payload_body = request.get_data()
    
    # Verify the signature
    print(f"\nVerifying signature...")
    if not verify_webhook_signature(payload_body, signature, WEBHOOK_SECRET):
        print("ERROR: Invalid signature! Webhook may not be from Hermes Health.")
        print("Make sure that the webhook secret matches the one in your Hermes Health settings.")
        return jsonify({"error": "Invalid signature"}), 401
    
    print("✓ Signature verified successfully")
    
    # Parse the JSON payload
    webhook_data = request.get_json()

    # Print full payload for debugging
    print("\n" + "-"*60)
    print("Full Webhook Payload:")
    print("-"*60)
    print(json.dumps(webhook_data, indent=2))
    
    # Return success response
    return jsonify({"status": "received"}), 200

@app.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    print(f"\nWaiting for webhooks...")
    
    # Run the Flask development server
    # NOTE: For production, use a proper WSGI server like gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)

