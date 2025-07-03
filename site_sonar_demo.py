import requests
import sys

# run with python site_sonar_demo.py input.pdf

# Configuration
DOMAIN = "https://api.hermeshealth.dev"
API_KEY = ""
PROJECT_ID = 1578441519

PATIENT_ID = 123411111

PATIENT = {
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "1990-01-01",
    "sex": "Male",
    "zipCode": "12345",
    "startDateOfService": "2020-01-01",
    "endDateOfService": "2020-01-01",
    "hipaaExpirationDate": "2020-01-01",
    "mobile": "123-456-7890",
    "socialSecurityNumber": "123-45-6789",
    "email": "john.doe@example.com",
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



