"""
HIPAA Check Demo Script
=======================

Purpose
-------
This script automates a HIPAA compliance check for a given PDF file via the
Hermes Health API. It will:

1. Authenticate with your API key
2. Request a pre-signed upload URL
3. Upload the PDF for processing
4. Poll the API until the check is complete
5. Fetch and pretty-print the JSON results
6. Download the processed file (e.g., annotated or OCR’d PDF)

Prerequisites
-------------
- Python 3.6+
- `requests` library (install via `pip install requests`)

Configuration
-------------
Edit the variables below:

    DOMAIN  = "https://api.hermeshealth.dev"  # Base API URL
    API_KEY = "<YOUR_API_KEY>"               # Your Hermes Health API key

Usage
-----
    python hipaa_check_demo.py <input_file>

Example
-------
    python hipaa_check_demo.py test_1.pdf

The processed PDF will be saved locally with prefix `ocr_`.

"""

import time           # add delays between status checks
import requests       # HTTP requests to the Hermes Health API
import sys            # access command-line arguments
import json           # parse and pretty-print JSON responses

# Configuration: set your API endpoint and API key here
DOMAIN = "https://api.hermeshealth.ai"
API_KEY = ""  # ← insert your API key here

if __name__ == "__main__":
    # 1) Read the input PDF filename from the command line
    input_file = sys.argv[1]

    # 2) Prepare the authorization header for all API calls
    hermes_headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # 3) Construct URL to initiate HIPAA check
    hermes_url = f"{DOMAIN}/v0/hipaa-check/{input_file}"

    # 4) Request a pre-signed upload URL
    upload_pre_signed_url_json = requests.put(
        hermes_url,
        headers=hermes_headers
    ).json()

    # 5) Upload the file bytes to the storage service
    response = requests.put(
        upload_pre_signed_url_json['uploadUrl'],
        headers=upload_pre_signed_url_json['headers'],
        data=open(input_file, "rb")
    )

    # 6) Poll the API until processing is complete
    while True:
        response = requests.head(hermes_url, headers=hermes_headers)
        print(response.headers['X-Progress'] + "%")  # show progress
        if response.status_code == 200:
            break
        time.sleep(15)

    # 7) Fetch the JSON results of the HIPAA check
    hipaa_check_output_json = requests.get(
        hermes_url,
        headers=hermes_headers
    ).json()

    # Pretty-print the 'check' section
    print(json.dumps(hipaa_check_output_json['check'], indent=2))

    # 8) Download the processed file (e.g., OCR’d or annotated PDF)
    download_response = requests.get(
        hipaa_check_output_json['downloadUrl']
    )

    # Extract filename from Content-Disposition header
    content_disposition = download_response.headers.get('Content-Disposition', '')
    filename_start = content_disposition.find('filename="') + 10
    filename_end = content_disposition.find('"', filename_start)
    download_filename = content_disposition[filename_start:filename_end]

    # 9) Save the downloaded bytes locally with an "ocr_" prefix
    with open(f"ocr_{download_filename}", "wb") as f:
        f.write(download_response.content)

    print(f"Processed file saved as ocr_{download_filename}")
