# Healthcare Management Prototype

A Python and Streamlit demonstration of patient, staff, administrator, and emergency-room workflows, using local CSV storage and fictional records.

## Features

- Patient registration, login, appointment booking, history, and demo bill status.
- Staff appointment schedules, visit logs, and bill generation.
- Administrator views for staff, patients, medication, device, and consumable inventory.
- ER view of appointments marked Emergency; severity is not inferred.
- Optional AI summarization of synthetic demo notes.
- A clearly labeled toy classifier trained on invented examples, included only as a programming demonstration.

## Quick start

Use Python 3.11 or 3.12. In the project directory:

```bash
python -m venv .venv
```

Activate it:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install dependencies and create fictional demo accounts:

```bash
python -m pip install -r requirements.txt
python seed_demo.py
python run_demo.py
```

The seed script asks you to choose a local password of at least 12 characters. Use that password with `demo_patient`, `demo_staff`, `demo_admin`, or `demo_er`.

The demo stores records in `data/demo/` and refuses to overwrite an existing populated demo. No existing `data/*.csv` records are copied into it. To use existing local data deliberately, run `python -m streamlit run app.py`; the default storage directory is `data/`.

## Optional AI feature

The app works without an API key or the OpenAI SDK. To enable the optional demo:

1. Install `requirements-ai.txt`.
2. Set `OPENAI_API_KEY` and `OPENAI_MODEL` in your local environment.
3. Use a model available to your project that supports Chat Completions.
4. Open a staff visit log, confirm it contains synthetic data, and request a summary.

That action sends the displayed summary and notes to OpenAI. Do not enter real patient information into this demo. Never commit a key or paste it into Python source. A `.env` file is not loaded automatically; use operating-system environment variables.

## Structure

| File | Purpose |
| --- | --- |
| `app.py` | Login state and dashboard routing |
| `auth.py` | Registration, password verification, and account construction |
| `models.py` | Domain objects |
| `storage.py` | Schema initialization and CSV read/write helpers |
| `services.py` | Shared history and billing operations |
| `modules/` | Patient, staff, admin, and ER interfaces |
| `seed_demo.py` | Fictional demo data generation |
| `run_demo.py` | Launch with the isolated demo directory |
| `tests/test_regressions.py` | Regression checks using temporary synthetic records |

## Validation

Run the business-logic checks from the project directory:

```bash
python -m unittest discover -s tests -v
```

The supplied fixes passed 14 regression checks during preparation. Streamlit was unavailable in that environment, so only its import was stubbed for these checks. Full browser behavior and live API calls were not tested. Complete the walkthrough in `APPLY_FIXES.md` before presenting the project.

## Limitations

- CSV persistence is intended for a local demonstration. Individual writes are atomic, but operations across files are not transactions; concurrent sessions can still conflict. Use a database and transaction-based operations before multi-user deployment.
- Payments are status changes only. The app does not process payments, generate receipts, or dispatch ambulances.
- The ML examples are unvalidated and provide no meaningful personal health assessment.
- Login has no rate limiting, password reset, or production session infrastructure. Publicly exposed legacy credentials must still be reset/revoked; automatic password-hash migration does not make a leaked password private again.
- The repository should contain only code and synthetic demo generation scripts, not real patient records or usable credentials.
