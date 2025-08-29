import requests
import sys
import json
# run with python record_request_demo.py input.pdf

# Configuration
DOMAIN = "https://api.hermeshealth.ai"
API_KEY = ""
PROJECT_ID = 456752830

PATIENT_ID = "CLIENT-54444"

#OPTIONAL IF THE PATIENT EXISTS
PATIENT = {
    "firstName": "Jane",
    "lastName": "Doe",
    "dateOfBirth": "1990-01-01",
    "sex": "Female",
    "startDateOfService": "2020-01-01",
    "endDateOfService": "2025-01-01",
    "hipaaExpirationDate": "2025-01-01",
    "mobile": "123-456-7890",
    "socialSecurityNumber": "123-45-6789",
    "email": "jane.doe@example.com",
}

# REQUIRED
SITE = {
    "siteName": "Ochsner Medical Center",
    "siteAddress": "1514 Jefferson Hwy",
    "siteCity": "Jefferson",
    "siteState": "LA",
    "siteZip": "70121"
}

PREVIOUS_REQUEST_ID = "298"


if __name__ == "__main__":
    hermes_headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    hipaa_authorization_filename = sys.argv[1]

    print(f"\nAdding patient: {PATIENT['firstName']} {PATIENT['lastName']}")
    print("-" * 50)
    
    upload_pre_signed_url_json = requests.put(
        f"{DOMAIN}/v0/projects/{PROJECT_ID}/patients/{PATIENT_ID}",
        headers=hermes_headers,
        json=PATIENT,
    ).json()

    requests.put(upload_pre_signed_url_json['uploadUrl'], headers=upload_pre_signed_url_json['headers'], data=open(hipaa_authorization_filename, "rb"))

    record_request_response_json = requests.post(
        f"{DOMAIN}/v0/projects/{PROJECT_ID}/patients/{PATIENT_ID}/record-requests",
        headers=hermes_headers,
        json=SITE,
    ).json()

    request_id = record_request_response_json["requestId"]
    print(f"Request ID: {request_id}")

    print("Fetching patient's previous request...")

    previous_request_url = f"{DOMAIN}/v0/projects/{PROJECT_ID}/patients/{PATIENT_ID}/record-requests/{PREVIOUS_REQUEST_ID}"
    previous_request_response_json = requests.get(
        previous_request_url,
        headers=hermes_headers,
    ).json()
    print(json.dumps(previous_request_response_json, indent=2))

    medical_record_url = previous_request_response_json["recordRequest"]["medicalRecordUrl"]

    if medical_record_url != None:
        print("Downloading medical record...")
        download_response = requests.get(medical_record_url)
        with open("medical_record.pdf", "wb") as f:
            f.write(download_response.content)
        print("Medical record downloaded")
    else:
        print("No medical record found")

