import requests
import json

# run with python site_sonar_demo.py

# Configuration
DOMAIN = "https://api.hermeshealth.dev"
API_KEY = ""
PROJECT_ID = 1578441519

TEST_PATIENTS = {
    "patient_1": {
        "firstName": "John",
        "lastName": "Doe",
        "dateOfBirth": "1990-01-01",
        "sex": "Male",
        "zipCode": "12345",
        "startDateOfService": "2020-01-01",
        "endDateOfService": "2020-01-01",
        "hipaaExpiration": "2020-01-01",
        "mobile": "123-456-7890",
        "socialSecurity": "123-45-6789",
        "email": "john.doe@example.com",
        "siteSonar": True,
    },
}


if __name__ == "__main__":
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for patient_id, patient in TEST_PATIENTS.items():
        print(f"\nAdding patient: {patient['firstName']} {patient['lastName']}")
        print("-" * 50)
        
        response = requests.put(
            f"{DOMAIN}/v0/projects/{PROJECT_ID}/patients/{patient_id}/hipaa-authorization",
            headers=headers,
            json=patient,
        )

        print(response.status_code)
        result = response.json()
        print(json.dumps(result, indent=2))



