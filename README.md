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

<img width="2870" height="1508" alt="image" src="https://github.com/user-attachments/assets/1a1757dd-e61e-40b0-96bc-49a4a4521411" />
<img width="2880" height="1496" alt="image2" src="https://github.com/user-attachments/assets/fd873e81-07f2-4773-8c50-a41e6550aad7" />
