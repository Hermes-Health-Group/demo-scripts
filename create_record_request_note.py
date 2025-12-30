# Hermes Health Record Request Note Demo Script
# ----------------------------------------------
# This script demonstrates how to:
# 1. Create a note on a record request
# 2. Fetch the record request and read its notes
#
# API Endpoints:
#   POST /v0/companies/{company_id}/projects/{project_id}/patients/{patient_id}/record-requests/{record_request_id}/notes
#   GET  /v0/companies/{company_id}/projects/{project_id}/patients/{patient_id}/record-requests/{record_request_id}
#
# Create Note Request Body (JSON):
#   - content (string, required): The text content of the note
#   - email (string, optional): Email of another user to impersonate when creating the note
#                               (requires ImpersonateUser permission)

import requests
import json

# Run with:
# python create_record_request_note.py

# --------------------
# Configuration values
# --------------------
DOMAIN = "https://api.hermeshealth.ai"  # Base Hermes Health API endpoint
API_KEY = ""  # Replace with your API key

COMPANY_ID = "1"  # Replace with your company ID
PROJECT_ID = "456752830"  # Replace with your project ID
PATIENT_ID = "CLIENT-54444"  # Replace with your patient ID
RECORD_REQUEST_ID = "298"  # Replace with your record request ID

# Note content to create
NOTE_CONTENT = "This is an example note on the record request."

# ------------------------
# Main program entry point
# ------------------------
if __name__ == "__main__":
    # Prepare request headers for Hermes Health API
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Build the endpoint URL
    url = f"{DOMAIN}/v0/companies/{COMPANY_ID}/projects/{PROJECT_ID}/patients/{PATIENT_ID}/record-requests/{RECORD_REQUEST_ID}/notes"

    # Build the request body
    payload = {
        "content": NOTE_CONTENT,
        # Optionally include "email" to impersonate another user (requires ImpersonateUser permission):
        # "email": "other.user@example.com"
    }

    print(f"Creating note on record request {RECORD_REQUEST_ID}...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)

    # Step 1: POST request to create the note
    response = requests.post(url, headers=headers, json=payload)

    # Check the response
    if response.status_code == 200:
        print("Note created successfully!")
    else:
        print(f"Failed to create note. Status code: {response.status_code}")
        print(f"Response: {response.text}")

    # Step 2: GET the record request to read its notes
    print()
    print("=" * 50)
    print("Fetching record request to read notes...")
    print("-" * 50)

    record_request_url = f"{DOMAIN}/v0/companies/{COMPANY_ID}/projects/{PROJECT_ID}/patients/{PATIENT_ID}/record-requests/{RECORD_REQUEST_ID}"
    response = requests.get(record_request_url, headers=headers)

    if response.status_code == 200:
        record_request = response.json()
        notes = record_request.get("notes", [])
        print(f"Found {len(notes)} note(s) on this record request:\n")
        for note in notes:
            print(f"  ID: {note.get('id')}")
            print(f"  User: {note.get('userName')}")
            print(f"  Created: {note.get('createdAt')}")
            print(f"  Content: {note.get('content')}")
            print()
    else:
        print(f"Failed to fetch record request. Status code: {response.status_code}")
        print(f"Response: {response.text}")
