# Apply the healthcare_app fixes

These files replace the application source reviewed on `master` at commit `9bb2a2950cc8b211430de6059e087dc6b716e522`. No GitHub changes have been made for you. If you have edited those files since that commit, compare your changes before replacing them.

## 1. Revoke the exposed key first

Open the [OpenAI API keys page](https://platform.openai.com/api-keys) and revoke the key that was embedded in `modules/staff_dashboard.py`. Check usage for unexpected activity. Do not paste the old key into this package or into a chat. The basic app does not need a replacement key.

Removing a key from the latest commit does not remove it from Git history and does not invalidate it. Revocation is required even if you later remove historical copies. See [OpenAI's key-safety guidance](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety).

## 2. Work on a cleanup branch

For a fresh local copy:

```bash
git clone --branch master https://github.com/HindAlz/healthcare_app.git healthcare-app-cleanup
cd healthcare-app-cleanup
git switch -c cleanup/healthcare-prototype
```

If you already have a local copy, save or commit your own changes first. Then switch to `master`, pull the latest version, and create the cleanup branch:

```bash
git status
git switch master
git pull --ff-only
git switch -c cleanup/healthcare-prototype
```

Use one of these routes, not both. If the branch name already exists, choose a new name.

## 3. Copy the replacement code into the repository

Extract `healthcare-replacements.zip`. Copy the **contents** of its `healthcare-replacements` folder into the repository folder (the folder containing the existing `app.py`). Agree to replace the matching files. Do not place the entire folder one level below the existing app.

Files to replace:

- `app.py`, `auth.py`, `models.py`
- `modules/admin_dashboard.py`
- `modules/patient_dashboard.py`
- `modules/staff_dashboard.py`
- `modules/er_dashboard.py`
- `ai/diabetes_checker.py`

Files to add, or carefully merge if you have created them recently:

- `storage.py`, `services.py`
- `seed_demo.py`, `run_demo.py`
- `requirements.txt`, `requirements-ai.txt`
- `.gitignore` (a hidden file on some systems)
- `tests/test_regressions.py`
- `README.md`, `APPLY_FIXES.md`

`storage.py` and `services.py` are required by the replacement dashboards. Copy the complete package before trying to run it. No model binaries, virtual environment, API credentials, or account records are included in the ZIP.

## 4. Stop tracking local environment and data files

In the repository terminal, run:

```bash
git rm -r --cached --ignore-unmatch venv .venv .idea __pycache__ pages/__pycache__ modules/__pycache__ ai/__pycache__
git rm --cached --ignore-unmatch data/users.csv data/appointments.csv data/medications.csv data/devices.csv data/consumables.csv data/bills.csv data/logs.csv data/medical_history.csv
```

`--cached` removes files from Git tracking but keeps the copies on your computer. The supplied `.gitignore` prevents them from being added again. The demo seed script supplies fictional replacements locally.

This cleans future commits; it does not shrink old history or erase historically published data. If any published records are real or any account passwords were reused elsewhere, address that exposure separately before sharing the portfolio. Do not assume deleting a CSV from the current branch removes all public copies.

## 5. Install and run the isolated demo

Create a new environment instead of reusing the committed Windows `venv`:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If your PowerShell settings prevent activation, use `.\.venv\Scripts\python.exe` in place of `python` in the remaining commands; changing execution policy is unnecessary.

macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python seed_demo.py
python run_demo.py
```

When seeding, choose a local demo password with at least 12 characters. It is shared by the four **fictional local demo accounts**: `demo_patient`, `demo_staff`, `demo_admin`, `demo_er`. Store it privately; it is not part of the code or README.

The script writes only to `data/demo/`, and refuses to overwrite a populated demo. If you already seeded successfully, skip `seed_demo.py` and run `python run_demo.py`.

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## 6. Check the workflows before sharing

1. Log in as `demo_patient`: view appointments, open empty billing/history screens, and update the profile. Log out.
2. Log in as `demo_staff`: add a fictional visit log for Demo Patient. Open the Checkup appointment, choose End & Bill, and confirm AED 200. Confirm and save. Log out.
3. Log in as `demo_patient`: confirm the visit log and AED 200 bill appear. Mark the bill paid; this is a simulation. Log out.
4. Log in as `demo_admin`: search by numeric ID and name, add a resource, and check its generated ID. Create a staff account using a normal password, not a manually generated hash.
5. Log in as `demo_er`: confirm the emergency appointment appears. Severity should say Not recorded; no ambulance is dispatched.
6. Register a second fictional patient and confirm that the first patient's history does not appear in that account.
7. Log out and log in as a different role. Confirm the previous user's patient selection or AI output does not remain visible.

The prepared regression checks passed, but the full Streamlit UI was not executed during preparation. If you see an error, keep the cleanup branch unmerged and capture the traceback without credentials.

## 7. Keep AI optional

No API key is required for steps 1–6. To use the optional synthetic-note summary later:

```bash
python -m pip install -r requirements-ai.txt
```

Set `OPENAI_API_KEY` to a new key and `OPENAI_MODEL` to a Chat Completions model available in your project using your computer's environment-variable settings. Restart the app after changing those values. Do not save a key in a Python file, commit it to Git, or use the revoked key.

The AI feature now summarizes fictional notes rather than presenting medical advice. It runs only when you explicitly click the button on a log and confirm synthetic data. The toy classifier remains clearly labeled as a programming demonstration trained on invented examples.

## 8. Review and commit

```bash
git status
git diff --stat
```

Confirm that `venv/`, cache files, and data CSVs are staged for removal from Git; your local copies should still exist. Confirm `.venv/`, `data/demo/`, `.env`, and any local secret files are absent from the files being added.

Stage only the prepared code and documentation:

```bash
git add app.py auth.py models.py storage.py services.py seed_demo.py run_demo.py requirements.txt requirements-ai.txt .gitignore README.md APPLY_FIXES.md
git add modules/admin_dashboard.py modules/patient_dashboard.py modules/staff_dashboard.py modules/er_dashboard.py ai/diabetes_checker.py tests/test_regressions.py
git diff --cached --stat
git commit -m "Repair demo workflows and remove tracked environment files"
git push -u origin cleanup/healthcare-prototype
```

If you chose another cleanup branch name, use it in the last command. On GitHub, create a pull request with base `master` and your cleanup branch as the comparison. Review it and merge after the local walkthrough succeeds.

## What the fixes change

| Problem | Replacement behavior |
| --- | --- |
| Hardcoded API credential | Key/model read from environment only when optional summary is requested |
| Shared default lists | Independent history/resource lists per object |
| ER login routed to staff | Explicit role identity and dashboard lookup |
| Signup fails on empty users | First numeric ID starts at 1 |
| Plain SHA-256 password storage | Salted PBKDF2 hashes; valid legacy logins upgrade automatically |
| Stale state between logins | Logout/login clears all account-specific session state |
| Missing CSV files | Empty schema-correct files created without overwriting existing records |
| Incorrect Checkup/Follow-up prices | Labels normalized before pricing; unknown types raise an error |
| New billing replaces old bills | Bills upserted by ID, preserving unrelated history |
| Duplicate end-and-bill requests | Existing bill reused for the same patient and appointment |
| History date and loading issues | Explicit accepted formats and patient-filtered reads |
| Resource creation lacks IDs | Unique resource IDs generated for new inventory records |
| ER dummy arrays fail with many cases | Arbitrary numbers of rows supported without fabricated severity/location |
| Unsupported medical/payment claims | Explicit toy ML, optional fictional-note summary, and payment simulation wording |

CSV storage still lacks cross-file transactions and concurrent-user protection. These fixes prepare a local demonstration, not a production healthcare service.
