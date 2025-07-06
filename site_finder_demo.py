"""
SITE FINDER DEMO SCRIPT
=======================

Purpose
-------
This script demonstrates how to use the Hermes Health Site Finder API to look up
healthcare facility records based on address data. It will:

1. Authenticate with your API key
2. Submit one or more test cases to the `/v0/site-finder` endpoint
3. Print the HTTP status code and pretty-print the JSON response for each case

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
    python site_finder_demo.py

Since this is a demo, the test cases are hard-coded in the script. You can
replace `TEST_CASES` or adapt the code to read from a file or other source.

Output
------
For each test case, you’ll see:

- The site name under test
- A line of separators
- The HTTP status code (e.g., `200` if found, `404` if not)
- The formatted JSON response from the API

"""

import requests
import json

# Configuration: set your API endpoint and API key here
DOMAIN = "https://api.hermeshealth.dev"
API_KEY = ""  # ← insert your API key here

# Demo test cases
TEST_CASES = [
    # This one should be found
    {
        "name": "Ochsner Medical Center",
        "address": "1514 Jefferson Hwy",
        "city": "Jefferson",
        "state": "LA",
        "zip": "70121"
    },
    # This one should not be found
    {
        "name": "Woman's Hospital",
        "address": "100 Woman's Way",
        "city": "Baton Rouge",
        "state": "LA",
        "zip": "70817"
    }
]

if __name__ == "__main__":
    # Prepare headers for JSON requests
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Iterate through each demo test case
    for test_case in TEST_CASES:
        print(f"\nTesting site: {test_case['name']}")
        print("-" * 50)

        # Call the Site Finder endpoint
        response = requests.post(
            f"{DOMAIN}/v0/site-finder",
            headers=headers,
            json=test_case
        )

        # Print status code and formatted JSON result
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
