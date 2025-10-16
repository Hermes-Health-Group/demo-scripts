import requests
import json
import sys

# Configuration
DOMAIN = "https://api.hermeshealth.ai"
API_KEY = ""

PROJECT_ID = "123ASDF"
COMPANY_ID = "1"

# Project data for creation
NEW_PROJECT = {
    "name": "Demo Project",
    "description": "A sample project for demonstration purposes",
    "medicalInformationRequested": ["Lab Results", "Imaging", "Progress Notes"]
}

# File paths for uploads (passed as command line arguments)
REQUEST_LETTER_FILE = sys.argv[1] if len(sys.argv) > 1 else None
REPRESENTATION_LETTER_FILE = sys.argv[2] if len(sys.argv) > 2 else None

if __name__ == "__main__":
    hermes_headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print("Creating new project...")
    print("-" * 50)
    
    # POST - Create a new project
    create_response = requests.put(
        f"{DOMAIN}/v0/companies/{COMPANY_ID}/projects/{PROJECT_ID}",
        headers=hermes_headers,
        json=NEW_PROJECT,
    )
    
    if create_response.status_code == 200:
        created_project = create_response.json()

        
        print(json.dumps(created_project, indent=2))

        print(f"Project created successfully!")
        print(f"Project ID: {PROJECT_ID}")
        print(f"Project Name: {created_project['project']['name']}")
        print(f"Description: {created_project['project']['description']}")
        print()
        
        # Upload request letter (if provided)
        if REQUEST_LETTER_FILE:
            print("Uploading request letter...")
            print("-" * 50)
            request_letter_upload = created_project["requestLetter"]
            with open(REQUEST_LETTER_FILE, "rb") as f:
                upload_response = requests.put(
                    request_letter_upload["uploadUrl"],
                    headers=request_letter_upload["uploadHeaders"],
                    data=f
                )
            print(f"Request letter upload status: {upload_response.status_code}")
        else:
            print("No request letter provided - skipping upload")
        
        # Upload representation letter (if provided)
        if REPRESENTATION_LETTER_FILE:
            print("Uploading representation letter...")
            print("-" * 50)
            representation_letter_upload = created_project["representationLetter"]
            with open(REPRESENTATION_LETTER_FILE, "rb") as f:
                upload_response = requests.put(
                    representation_letter_upload["uploadUrl"],
                    headers=representation_letter_upload["uploadHeaders"],
                    data=f
                )
            print(f"Representation letter upload status: {upload_response.status_code}")
        else:
            print("No representation letter provided - skipping upload")
        print()
        
        # GET - Retrieve the created project
        print("Retrieving project details...")
        print("-" * 50)
        
        get_response = requests.get(
            f"{DOMAIN}/v0/companies/{COMPANY_ID}/projects/{PROJECT_ID}",
            headers=hermes_headers,
        )
        
        if get_response.status_code == 200:
            project_details = get_response.json()
            print("Project details:")
            print(json.dumps(project_details, indent=2))
        else:
            print(f"Failed to retrieve project: {get_response.status_code}")
    else:
        print(f"Failed to create project: {create_response.status_code}")
        print(create_response.text)
