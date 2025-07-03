import requests
import json

# run with python site_finder_demo.py

# Configuration
DOMAIN = "https://api.hermeshealth.dev"
API_KEY = ""

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
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for test_case in TEST_CASES:
        print(f"\nTesting site: {test_case['name']}")
        print("-" * 50)
        
        response = requests.post(
            f"{DOMAIN}/v0/site-finder",
            headers=headers,
            json=test_case
        )

        print(response.status_code)
        result = response.json()
        print(json.dumps(result, indent=2))
