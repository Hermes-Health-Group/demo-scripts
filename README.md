# Hermes Health — Demo Scripts

Small, runnable Python demos that show how to use Hermes Health’s APIs and utilities for common workflows like finding facilities, validating HIPAA authorizations, submitting record requests, basic OCR, and simple patient/project operations.

> **Who is this for?**  
> Sales engineers, partners, and evaluators who want a hands-on feel for the endpoints and data structures without wiring up a full app.

---

## What’s inside

- `site_finder_demo.py` – Look up facilities/providers by patient or query parameters.
- `hipaa_check_demo.py` – Validate a HIPAA authorization (structure, dates, signatures).
- `record_request_demo.py` – Create/track a records request end-to-end.
- `ocr_demo.py` – OCR a sample doc and extract key fields for downstream checks.
- `patient_demo.py` – Basic patient object CRUD / fetch examples.
- `project_demo.py` – Lightweight project container examples (grouping requests/patients).

> File list reflects the current repo contents; see each script’s `--help` for flags.

---

## Prerequisites

- **Python** 3.10+ recommended  
- **Hermes Health API access** (base URL + API key)  
- macOS/Linux/WSL are easiest; Windows works too.

---

## Quickstart

```bash
# 1) Clone
git clone https://github.com/Hermes-Health-Group/demo-scripts.git
cd demo-scripts

# 2) Create a virtual env
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3) Install deps
# If requirements.txt exists:
pip install -r requirements.txt
# If not, install what you need per script (requests, python-dotenv, etc.)

# 4) Configure environment
cp .env.example .env   # then edit .env with your values
# or export directly:
export HERMES_API_KEY="your_key_here"
export HERMES_BASE_URL="https://api.hermeshealth.com"
