# Hermes Health Record Request Demo Script
# ----------------------------------------
# This script demonstrates how to:
# 1. Add or update a patient record in Hermes Health.
# 2. Upload the patient’s HIPAA authorization PDF.
# 3. Submit a new record request to a specified facility.
# 4. Fetch and inspect details of a previous record request.
# 5. Download the returned medical record if available.

import requests
import sys
import json

# Run with:
# python record_request_demo.py test_1.pdf
# where "input.pdf" is the HIPAA authorization PDF.

# --------------------
# Configuration values
# --------------------
DOMAIN = "https://api.hermeshealth.ai"  # Base Hermes Health API endpoint
API_KEY = ""  # Replace with your API key
PROJECT_ID = 456752830  # Replace with your project ID

PATIENT_ID = "CLIENT-54444"  # Client-assigned unique patient ID

# Patient metadata (OPTIONAL if patient already exists)
PATIENT = {
    "firstName": "Jane",
    "lastName": "Doe",
    "dateOfBirth": "1990-01-01",
    "sex": "female", # can be male | female | unknown or M | F | U
    "startDateOfService": "2020-01-01",   # Start of care window
    "endDateOfService": "2025-01-01",     # End of care window
    "hipaaExpirationDate": "2025-01-01",  # HIPAA authorization expiration
    "mobile": "123-456-7890",
    "socialSecurityNumber": "123-45-6789",
    "email": "jane.doe@example.com",
}

# Facility (site) metadata (REQUIRED for record request)
SITE = {
    "siteName": "Ochsner Medical Center",
    "siteAddress": "1514 Jefferson Hwy",
    "siteCity": "Jefferson",
    "siteState": "LA",
    "siteZip": "70121"
}

# Example of a previously created record request ID
PREVIOUS_REQUEST_ID = "298"
COMPANY_ID = "1"
REQUEST_ID = "ASDF123"

# ------------------------
# Main program entry point
# ------------------------
if __name__ == "__main__":
    # Prepare request headers for Hermes Health API
    hermes_headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # First CLI argument = HIPAA PDF filename
    hipaa_authorization_filename = sys.argv[1]

    # Step 1: Create or update patient record
    print(f"\nAdding patient: {PATIENT['firstName']} {PATIENT['lastName']}")
    print("-" * 50)
    
    upload_pre_signed_url_json = requests.put(
        f"{DOMAIN}/v0/companies/{COMPANY_ID}/projects/{PROJECT_ID}/patients/{PATIENT_ID}",
        headers=hermes_headers,
        json=PATIENT,
    ).json()

    print(json.dumps(upload_pre_signed_url_json, indent=2))

    # Step 2: Upload HIPAA authorization PDF to S3 pre-signed URL
    requests.put(
        upload_pre_signed_url_json['hipaaAuthorization']['uploadUrl'],
        headers=upload_pre_signed_url_json['hipaaAuthorization']['uploadHeaders'],
        data=open(hipaa_authorization_filename, "rb")
    )

    # Step 3: Submit new record request to the specified site
    requests.post(
        f"{DOMAIN}/v0/companies/{COMPANY_ID}/projects/{PROJECT_ID}/patients/{PATIENT_ID}/record-requests/{REQUEST_ID}",
        headers=hermes_headers,
        json=SITE,
    ).json()

    # Step 4: Retrieve details of a previous record request
    print("Fetching patient's previous request...")
    previous_request_response_json = requests.get(
        f"{DOMAIN}/v0/companies/{COMPANY_ID}/projects/{PROJECT_ID}/patients/{PATIENT_ID}/record-requests/{PREVIOUS_REQUEST_ID}",
        headers=hermes_headers,
    ).json()
    print(json.dumps(previous_request_response_json, indent=2))

    # Step 5: If medical record file is available, download it
    medical_record_url = previous_request_response_json["medicalRecord"]["downloadUrl"]

    if medical_record_url is not None:
        print("Downloading medical record...")
        download_response = requests.get(medical_record_url)
        with open("medical_record.pdf", "wb") as f:
            f.write(download_response.content)
        print("Medical record downloaded")
    else:
        print("No medical record found")
