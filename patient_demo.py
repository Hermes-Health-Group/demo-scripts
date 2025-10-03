# Hermes Health Patient Upload & Site Sonar Script
# ------------------------------------------------
# This script demonstrates how to:
# 1. Add a patient to a project on Hermes Health.
# 2. Upload the patient’s HIPAA authorization PDF.
# 3. Trigger Site Sonar to discover facilities tied to the patient.
# 4. Print out facility metadata returned by the API.

import requests
import sys
import json

# Run the script with:
# python patient_demo.py test_1.pdf

# --------------------
# Configuration values
# --------------------
DOMAIN = "https://api.hermeshealth.ai"  # Base API domain
API_KEY = ""  # Replace with your Hermes Health API key
PROJECT_ID = 456752830  # Replace with your project ID
COMPANY_ID = 1
PATIENT_ID = "example-321"  # Unique patient identifier (set by client)
PREVIOUS_PATIENT_ID = "example-123"  # Unique patient identifier (set by client)

# Patient demographic and HIPAA-related metadata
PATIENT = {
    "firstName": "Alejandro",
    "lastName": "Franco",
    "dateOfBirth": "1990-01-01",
    "sex": "Female",
    "zipCode": "12345",
    "startDateOfService": "2020-01-01",   # Start of care window
    "endDateOfService": "2025-01-01",     # End of care window
    "hipaaExpirationDate": "2025-01-01",  # HIPAA authorization expiration
    "mobile": "123-456-7890",
    "socialSecurityNumber": "123-45-6789",
    "email": "jane.doe@example.com",
    "siteSonar": True,  # Enable Site Sonar to find facilities automatically
}

# ------------------------
# Main program entry point
# ------------------------
if __name__ == "__main__":
    # Prepare HTTP headers for Hermes Health API
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Step 1: Add patient to the project
    print(f"\nAdding patient: {PATIENT['firstName']} {PATIENT['lastName']}")
    print("-" * 50)
    
    # PUT request to create or update a patient record
    upload_pre_signed_url_json = requests.put(
        f"{DOMAIN}/v0/companies/{COMPANY_ID}/projects/{PROJECT_ID}/patients/{PATIENT_ID}",
        headers=headers,
        json=PATIENT,
    ).json()

    
    print(json.dumps(upload_pre_signed_url_json, indent=2))

    # Step 2: Upload HIPAA authorization PDF
    # The file path is passed as the first argument when running the script
    hipaa_authorization_filename = sys.argv[1]
    requests.put(
        upload_pre_signed_url_json['hipaaAuthorization']['uploadUrl'],  # Pre-signed S3 URL
        headers=upload_pre_signed_url_json['hipaaAuthorization']['uploadHeaders'],  # Required headers
        data=open(hipaa_authorization_filename, "rb")  # File stream
    )

    # Step 3: Trigger Site Sonar to retrieve facilities for this patient
    # This takes 12-48 hours, so we will retrieve a previous patient's as an example
    site_sonar_response_json = requests.get(
        f"{DOMAIN}/v0/companies/{COMPANY_ID}/projects/{PROJECT_ID}/patients/{PREVIOUS_PATIENT_ID}/site-sonar?columns=patient~siteSonar&flatten",
        headers=headers
    ).json()
        
    # Step 4: Pretty-print the Site Sonar JSON response
    print(json.dumps(site_sonar_response_json, indent=2))
