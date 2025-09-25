"""
README
======

Purpose
-------
This script automates uploading a document to the Hermes Health API for processing
(either OCR-PDF or OCR-JSON), polls the API until the processing is complete, and
then downloads the resulting file.

Usage
-----
    python 1_api_documents.py <processing_type> <input_file>
    
    - processing_type: “ocr-pdf” or “ocr-json”
    - input_file:        Path to the PDF you wish to process (e.g. “ocr_test_1.pdf”)

Example
-------
    python 1_api_documents.py ocr-pdf ocr_test_1.pdf
    python 1_api_documents.py ocr-json ocr_test_1.pdf

Requirements
------------
    - Python 3.x
    - requests library (install via `pip install requests`)

Configuration
-------------
    - DOMAIN:   Base URL for the Hermes Health API
    - API_KEY:  Your authentication key (set below)

"""

import time              # for sleep() between polling attempts
import requests          # for HTTP requests (upload, polling, download)
import sys               # for reading command-line arguments

# Usage examples:
# python ocr_demo.py ocr-pdf test_3.pdf
# python ocr_demo.py ocr-json test_3.pdf

# Configuration: set your API host and key here
DOMAIN = "https://api.hermeshealth.ai"
API_KEY = ""  # ← insert your API key

if __name__ == "__main__":
    # Read command-line args: processing_type (endpoint) and input_file (to upload)
    input_file = sys.argv[1]        # e.g. "ocr_test_1.pdf"

    # Prepare the Authorization header for all requests
    hermes_headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Construct the URL for initiating upload/processing
    hermes_url = f"{DOMAIN}/v0/ocr/{input_file}"

    # Step 1: Request a pre-signed upload URL for the file
    upload_pre_signed_url_json = requests.put(
        hermes_url,
        headers=hermes_headers
    ).json()

    # Step 2: Upload the file bytes to the pre-signed URL
    requests.put(
        upload_pre_signed_url_json['uploadUrl'],
        headers=upload_pre_signed_url_json['headers'],
        data=open(input_file, "rb")
    )

    # Step 3: Poll the processing endpoint until it’s done
    while True:
        # HEAD request returns progress percentage in the X-Progress header
        response = requests.head(hermes_url, headers=hermes_headers)
        print(response.headers['X-Progress'] + "%")  # e.g. "25%"

        # When status code is 200, processing is complete
        if response.status_code == 200:
            break

        # Wait before polling again to avoid spamming the API
        time.sleep(15)

    # Step 4: Once done, request a pre-signed download URL for the result
    download_pre_signed_url_json = requests.get(
        hermes_url,
        headers=hermes_headers
    ).json()

    # Step 5: Download the processed file from the pre-signed URL
    download_response = requests.get(download_pre_signed_url_json['downloadUrl'])

    # Extract the filename from the Content-Disposition header
    content_disposition = download_response.headers.get('Content-Disposition', '')
    filename_start = content_disposition.find('filename="') + 10
    filename_end = content_disposition.find('"', filename_start)
    download_filename = content_disposition[filename_start:filename_end]

    # Step 6: Save the downloaded content locally, prefixing with the processing type
    output_path = f"ocr_{download_filename}"
    with open(output_path, "wb") as f:
        f.write(download_response.content)

    print(f"Downloaded result saved to: {output_path}")
