import time
import requests
import sys
import json

# python hipaa_check_demo.py input.pdf

# Configuration
DOMAIN = "https://api.hermeshealth.dev" 
API_KEY = ""


if __name__ == "__main__":
    input_file = sys.argv[1]
    hermes_headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    hermes_url = f"{DOMAIN}/v0/hipaa-check/{input_file}"

    upload_pre_signed_url_json = requests.put(
        hermes_url,
        headers=hermes_headers
    ).json()

    requests.put(upload_pre_signed_url_json['uploadUrl'], headers=upload_pre_signed_url_json['headers'], data=open(input_file, "rb"))

    while True:
        response = requests.head(hermes_url, headers=hermes_headers)
        print(response.headers['X-Progress'] + "%")
        if response.status_code == 200:
            break
        time.sleep(15)
    
    hipaa_check_output_json = requests.get(
        hermes_url,
        headers=hermes_headers
    ).json()

    print(json.dumps(hipaa_check_output_json['check'], indent=2))

    download_response = requests.get(hipaa_check_output_json['downloadUrl'])

    content_disposition = download_response.headers.get('Content-Disposition', '')
    
    filename_start = content_disposition.find('filename="') + 10
    filename_end = content_disposition.find('"', filename_start)
    download_filename = content_disposition[filename_start:filename_end]
    
    with open(f"ocr_{download_filename}", "wb") as f:
        f.write(download_response.content)
    
