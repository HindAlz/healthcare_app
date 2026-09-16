"""CSV storage for a local, single-process demonstration (not a production database)."""
import os
import tempfile
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
configured = Path(os.environ.get('HEALTHCARE_DATA_DIR', 'data/demo'))
DATA_DIR = configured if configured.is_absolute() else PROJECT_DIR / configured
SCHEMAS = {
    'users.csv': ['user_id', 'username', 'password', 'role', 'name', 'birthday', 'email', 'position', 'specialization', 'schedule'],
    'appointments.csv': ['appointment_id', 'date', 'time', 'patient_id', 'staff_id', 'type', 'meeting_link'],
    'bills.csv': ['bill_id', 'patient_id', 'appointment_id', 'amount', 'status'],
    'logs.csv': ['patient_id', 'date', 'summary', 'details'],
    'medical_history.csv': ['patient_id', 'date', 'summary'],
    'medications.csv': ['med_id', 'name', 'stock', 'expiry', 'low_stock'],
    'devices.csv': ['device_id', 'name', 'available', 'next_maintenance', 'low_available'],
    'consumables.csv': ['consumable_id', 'name', 'stock', 'expiry', 'low_stock'],
}
NUMERIC_COLUMNS = {'user_id', 'patient_id', 'staff_id', 'appointment_id', 'amount', 'stock', 'available', 'low_stock', 'low_available'}

def table_path(filename):
    name = Path(filename).name
    if name not in SCHEMAS:
        raise ValueError(f'Unknown data table: {name}')
    return DATA_DIR / name

def ensure_data_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, columns in SCHEMAS.items():
        path = table_path(name)
        # Exclusive creation preserves existing data, including intentionally empty tables.
        try:
            with path.open('x', encoding='utf-8', newline='') as handle:
                pd.DataFrame(columns=columns).to_csv(handle, index=False)
        except FileExistsError:
            pass

def read_table(filename):
    ensure_data_files()
    name = Path(filename).name
    try:
        df = pd.read_csv(table_path(name), dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=SCHEMAS[name])
    # Preserve additional columns, but provide missing optional columns to callers.
    for column in SCHEMAS[name]:
        if column not in df:
            df[column] = ''
    for column in NUMERIC_COLUMNS.intersection(df.columns):
        df[column] = pd.to_numeric(df[column].replace('', pd.NA), errors='raise')
    return df

def write_table(df, filename):
    ensure_data_files()
    path = table_path(filename)
    output = df.copy()
    for column in SCHEMAS[path.name]:
        if column not in output:
            output[column] = ''
    fd, temporary = tempfile.mkstemp(dir=DATA_DIR, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as handle:
            output.to_csv(handle, index=False)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def next_numeric_id(df, column):
    values = pd.to_numeric(df[column], errors='coerce').dropna()
    return int(values.max()) + 1 if not values.empty else 1
