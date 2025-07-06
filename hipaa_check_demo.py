import time           # to add delays between status checks
import requests       # for HTTP requests to the Hermes Health API
import sys            # to access command-line arguments
import json           # to parse and pretty-print JSON responses

# Usage:
#   python hipaa_check_demo.py test_1.pdf

# Configuration: set your API endpoint and API key here
DOMAIN = "https://api.hermeshealth.dev"
API_KEY = ""

if __name__ == "__main__":
    # Grab the input filename from the first command-line argument
    input_file = sys.argv[1]

    # Prepare the authorization header for all API calls
    hermes_headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Construct the URL to initiate a HIPAA check on the given file
    hermes_url = f"{DOMAIN}/v0/hipaa-check/{input_file}"

    # 1) Request a pre-signed upload URL from the API
    upload_pre_signed_url_json = requests.put(
        hermes_url,
        headers=hermes_headers
    ).json()

    # 2) Upload the file bytes directly to the storage service
    requests.put(
        upload_pre_signed_url_json['uploadUrl'],
        headers=upload_pre_signed_url_json['headers'],
        data=open(input_file, "rb")
    )

    # 3) Poll the API until processing is complete
    while True:
        response = requests.head(
            hermes_url,
            headers=hermes_headers
        )
        # Print progress percentage returned in the X-Progress header
        print(response.headers['X-Progress'] + "%")
        # Exit loop once the API returns HTTP 200 (done)
        if response.status_code == 200:
            break
        # Wait before polling again to avoid spamming the API
        time.sleep(15)

    # 4) Fetch the final HIPAA check results as JSON
    hipaa_check_output_json = requests.get(
        hermes_url,
        headers=hermes_headers
    ).json()

    # Pretty-print the 'check' portion of the response
    print(json.dumps(hipaa_check_output_json['check'], indent=2))

    # 5) Download the processed file (e.g., OCR or annotated PDF)
    download_response = requests.get(
        hipaa_check_output_json['downloadUrl']
    )

    # Extract the filename from the Content-Disposition header
    content_disposition = download_response.headers.get('Content-Disposition', '')
    filename_start = content_disposition.find('filename="') + 10
    filename_end = content_disposition.find('"', filename_start)
    download_filename = content_disposition[filename_start:filename_end]

    # Save the downloaded bytes to disk, prefixing with "ocr_"
    with open(f"ocr_{download_filename}", "wb") as f:
        f.write(download_response.content)
