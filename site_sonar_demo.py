import requests
import sys
import json

# run with python site_sonar_demo.py input.pdf

# Configuration
DOMAIN = "https://api.hermeshealth.dev"
API_KEY = ""
PROJECT_ID = 84371101

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
        f"{DOMAIN}/v0/projects/{PROJECT_ID}/patients/{PATIENT_ID}/hipaa-authorization",
        headers=headers,
        json=PATIENT,
    ).json()

    hipaa_authorization_filename = sys.argv[1]
    requests.put(upload_pre_signed_url_json['uploadUrl'], headers=upload_pre_signed_url_json['headers'], data=open(hipaa_authorization_filename, "rb"))

    # get the results (should be empty right now, this takes at least a day)
    site_sonar_response = requests.get(f"{DOMAIN}/v0/projects/{PROJECT_ID}/patients/{PATIENT_ID}/site-sonar", headers=headers)
    
    print(json.dumps(site_sonar_response.json(), indent=2))