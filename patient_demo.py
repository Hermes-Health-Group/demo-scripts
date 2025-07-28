'''
# Hermes Health Patient Upload & Site Sonar Script

This script allows you to:

1. Add a patient to a specific project on the Hermes Health platform.
2. Upload the patient's HIPAA authorization PDF.
3. Automatically trigger Site Sonar to discover facilities associated with the patient.
4. Print facility metadata for each identified site.

## Prerequisites

- Python 3.x
- `requests` library
- A valid `API_KEY` for Hermes Health
- A valid `PROJECT_ID` on the Hermes Health platform
- A HIPAA authorization PDF file for the patient

## Setup

1. Clone or download this script.
2. Install the `requests` package if not already installed:

```bash
pip install requests
'''

import requests
import sys
import json

# run with python patient_demo.py input.pdf

# Configuration
DOMAIN = "https://api.hermeshealth.ai"
API_KEY = ""
PROJECT_ID = 456752830

PATIENT_ID = "CLIENT-54444"

PATIENT = {
    "firstName": "Jane",
    "lastName": "Doe",
    "dateOfBirth": "1990-01-01",
    "sex": "Female",
    "zipCode": "12345",
    "startDateOfService": "2020-01-01",
    "endDateOfService": "2025-01-01",
    "hipaaExpirationDate": "2025-01-01",
    "mobile": "123-456-7890",
    "socialSecurityNumber": "123-45-6789",
    "email": "jane.doe@example.com",
    "siteSonar": True,
}


if __name__ == "__main__":
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"\nAdding patient: {PATIENT['firstName']} {PATIENT['lastName']}")
    print("-" * 50)
    
    upload_pre_signed_url_json = requests.put(
        f"{DOMAIN}/v0/projects/{PROJECT_ID}/patients/{PATIENT_ID}",
        headers=headers,
        json=PATIENT,
    ).json()

    hipaa_authorization_filename = sys.argv[1]
    requests.put(upload_pre_signed_url_json['uploadUrl'], headers=upload_pre_signed_url_json['headers'], data=open(hipaa_authorization_filename, "rb"))

    site_sonar_response_json = requests.get(f"{DOMAIN}/v0/projects/{PROJECT_ID}/patients/{PATIENT_ID}/site-sonar", headers=headers).json()
        
    print(json.dumps(site_sonar_response_json, indent=2))

    sites = site_sonar_response_json["sites"]

    for site in sites:
        site_id = site["siteId"]
        if site_id == None: continue
        print(f"Getting info for site ID: {site_id}")

        site_sonar_response_json = requests.get(f"{DOMAIN}/v0/sites/{site_id}", headers=headers).json()

        print(json.dumps(site_sonar_response_json, indent=2))



