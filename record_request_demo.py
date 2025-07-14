import time
import requests
import sys
import json
# run with python record_request_demo.py input.pdf

# Configuration
DOMAIN = "https://api.hermeshealth.dev"
API_KEY = ""
PROJECT_ID = 456752830

PATIENT_ID = "1234567890"
PATIENT = {
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "1990-01-01",
    "sex": "Male",
    "startDateOfService": "2020-01-01",
    "endDateOfService": "2020-01-01",
    "hipaaExpirationDate": "2020-01-01",
    "mobile": "123-456-7890",
    "socialSecurityNumber": "123-45-6789",
    "email": "john.doe@example.com",
}
SITE = {
    "siteName": "Ochsner Medical Center",
    "siteAddress": "1514 Jefferson Hwy",
    "siteCity": "Jefferson",
    "siteState": "LA",
    "siteZip": "70121"
}


if __name__ == "__main__":
    hermes_headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    hipaa_authorization_filename = sys.argv[1]

    print(f"\nAdding patient: {PATIENT['firstName']} {PATIENT['lastName']}")
    print("-" * 50)
    
    upload_pre_signed_url_json = requests.put(
        f"{DOMAIN}/v0/projects/{PROJECT_ID}/patients/{PATIENT_ID}/hipaa-authorization",
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
    print("Validating information in HIPAA Authorization")
    hipaa_url = f"{DOMAIN}/v0/projects/{PROJECT_ID}/patients/{PATIENT_ID}/hipaa-authorization"
    while True:
        response = requests.head(hipaa_url, headers=hermes_headers)
        print(response.headers['X-Progress'] + "%")
        if response.status_code == 200:
            break
        time.sleep(15)
    
    hipaa_check_output_json = requests.get(
        hipaa_url,
        headers=hermes_headers,
    ).json()

    print(json.dumps(hipaa_check_output_json['check'], indent=2))

