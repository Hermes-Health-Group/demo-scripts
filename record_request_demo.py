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
4. Poll the API until the analysis is complete
5. Fetch and pretty-print the JSON results
6. Download the processed file (e.g., annotated or OCR'd PDF)

Prerequisites
-------------
- Python 3.6+
- `requests` library (install via `pip install requests`)

Configuration
-------------
Edit the variables below:

    DOMAIN  = "https://api.hermeshealth.ai"  # Base API URL
    API_KEY = "<YOUR_API_KEY>"               # Your Hermes Health API key

Usage
-----
    python hipaa_check_demo.py <input_file> --first-name Jane --last-name Doe --dob 1990-01-15

Required flags:
    --first-name     Patient first name
    --last-name      Patient last name
    --dob            Patient date of birth (YYYY-MM-DD)

Optional flags:
    --type           Authorization type: Hipaa (default) or Hitech
    --capacity       Patient capacity: SelfAuthorizing (default), Deceased, Minor,
                     Comatose, CognitivelyImpaired, LegallyIncapacitated, PowerOfAttorney
    --start-date     Start date of service (YYYY-MM-DD)
    --end-date       End date of service (YYYY-MM-DD)
    --expiration     HIPAA expiration date (YYYY-MM-DD)
    --domain         API base URL (default: https://api.hermeshealth.ai)
    --api-key        API key (overrides the DOMAIN/API_KEY variables)

Example
-------
    python hipaa_check_demo.py hipaa_input.pdf \\
        --first-name Justin --last-name Howard --dob 1987-12-18

The processed PDF will be saved locally with prefix `ocr_`.
"""

import argparse
import json
import sys
import time

import requests

DOMAIN = "https://api.hermeshealth.ai"
API_KEY = ""  # ← insert your API key here

POLL_INTERVAL_SECONDS = 5
POLL_TIMEOUT_SECONDS = 120


def parse_args():
    parser = argparse.ArgumentParser(description="Run a HIPAA compliance check via the Hermes Health API.")
    parser.add_argument("input_file", help="Path to the PDF file to check")
    parser.add_argument("--first-name", required=True, help="Patient first name")
    parser.add_argument("--last-name", required=True, help="Patient last name")
    parser.add_argument("--dob", required=True, help="Patient date of birth (YYYY-MM-DD)")
    parser.add_argument("--type", default="Hipaa", choices=["Hipaa", "Hitech"], help="Authorization type (default: Hipaa)")
    parser.add_argument("--capacity", default="SelfAuthorizing",
                        choices=["SelfAuthorizing", "Deceased", "Minor", "Comatose",
                                 "CognitivelyImpaired", "LegallyIncapacitated", "PowerOfAttorney"],
                        help="Patient capacity (default: SelfAuthorizing)")
    parser.add_argument("--start-date", default=None, help="Start date of service (YYYY-MM-DD)")
    parser.add_argument("--end-date", default=None, help="End date of service (YYYY-MM-DD)")
    parser.add_argument("--expiration", default=None, help="HIPAA expiration date (YYYY-MM-DD)")
    parser.add_argument("--domain", default=None, help="API base URL")
    parser.add_argument("--api-key", default=None, help="API key")

    return parser.parse_args()


def main():
    args = parse_args()

    domain = args.domain or DOMAIN
    api_key = args.api_key or API_KEY
    if not api_key:
        print("Error: no API key provided. Set API_KEY in the script or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    auth_headers = {"Authorization": f"Bearer {api_key}"}
    input_file = args.input_file
    filename = input_file.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    endpoint = f"{domain}/v0/hipaa-check/{filename}"

    # 1) Get a pre-signed upload URL
    print(f"Requesting upload URL for {input_file}...")
    response = requests.get(endpoint, headers=auth_headers)
    if response.status_code != 200:
        print(f"Error: GET {endpoint} returned {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)

    upload_info = response.json()
    upload_url = upload_info["uploadUrl"]
    upload_headers = {
        key: value
        for key, value in (upload_info.get("uploadHeaders") or {}).items()
        if value is not None
    }

    # 2) Upload the PDF to S3
    print("Uploading PDF...")
    with open(input_file, "rb") as pdf_file:
        put_response = requests.put(upload_url, data=pdf_file, headers=upload_headers)

    if put_response.status_code not in (200, 201):
        print(f"Error: S3 upload returned {put_response.status_code}: {put_response.text}", file=sys.stderr)
        sys.exit(1)

    print("Upload complete. Waiting for analysis...")

    # 3) Build patient data for the comparison checks
    patient_data = {
        "firstName": args.first_name,
        "lastName": args.last_name,
        "dateOfBirth": args.dob,
        "authorizationType": args.type,
        "capacity": args.capacity,
    }
    if args.start_date:
        patient_data["startDateOfService"] = args.start_date
    if args.end_date:
        patient_data["endDateOfService"] = args.end_date
    if args.expiration:
        patient_data["hipaaExpirationDate"] = args.expiration

    # 4) Poll until analysis is complete
    elapsed = 0
    while elapsed < POLL_TIMEOUT_SECONDS:
        response = requests.post(endpoint, headers=auth_headers, json=patient_data)
        if response.status_code != 200:
            print(f"Error: POST {endpoint} returned {response.status_code}: {response.text}", file=sys.stderr)
            sys.exit(1)

        result = response.json()
        analysis = result.get("analysis")
        if analysis and analysis.get("hipaaCheck"):
            break

        print(f"  Analysis not ready yet ({elapsed}s elapsed), retrying in {POLL_INTERVAL_SECONDS}s...")
        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed += POLL_INTERVAL_SECONDS
    else:
        print(f"Error: analysis did not complete within {POLL_TIMEOUT_SECONDS}s.", file=sys.stderr)
        sys.exit(1)

    # 5) Pretty-print the analysis
    print("\n=== Analysis Results ===\n")
    print(json.dumps(result["analysis"], indent=2))

    # 6) Download the processed PDF
    download_url = result.get("downloadUrl")
    if not download_url:
        print("\nNo download URL in response; skipping PDF download.")
        return

    download_response = requests.get(download_url)
    content_disposition = download_response.headers.get("Content-Disposition", "")

    if 'filename="' in content_disposition:
        filename_start = content_disposition.index('filename="') + 10
        filename_end = content_disposition.index('"', filename_start)
        download_filename = content_disposition[filename_start:filename_end]
    else:
        download_filename = input_file

    output_path = f"ocr_{download_filename}"
    with open(output_path, "wb") as output_file:
        output_file.write(download_response.content)

    print(f"\nProcessed file saved as {output_path}")


if __name__ == "__main__":
    main()
