"""Shared operations for the local demonstration."""
import re
import uuid
from datetime import datetime
import pandas as pd
from models import Bill
from storage import read_table, write_table

def parse_history_date(value):
    for pattern in ('%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(str(value).strip(), pattern).date()
        except ValueError:
            pass
    raise ValueError('History dates must be YYYY-MM-DD or DD-MM-YYYY.')

def history_for(patient_id):
    logs = read_table('logs.csv')
    legacy = read_table('medical_history.csv')
    rows = pd.concat([logs, legacy], ignore_index=True).fillna('')
    result = []
    for _, row in rows[rows['patient_id'] == patient_id].iterrows():
        date = parse_history_date(row['date'])
        result.append({'date': date.strftime('%d-%m-%Y'), 'details': row['summary']})
    return result

def save_bills(bills):
    """Upsert changed bills without removing unrelated historical bills."""
    if isinstance(bills, Bill):
        bills = [bills]
    if not bills:
        return
    current = read_table('bills.csv')
    new = pd.DataFrame([{'bill_id': str(b.billID), 'patient_id': b.patientID,
                         'appointment_id': b.appointmentID, 'amount': b.amount,
                         'status': 'Paid' if b.paid else 'Unpaid'} for b in bills])
    current = current[~current['bill_id'].isin(new['bill_id'])]
    write_table(pd.concat([current, new], ignore_index=True), 'bills.csv')

def calculate_bill(appointment_type, insurance_level='none'):
    # Ignore spacing and punctuation so UI labels and stored legacy labels agree.
    kind = re.sub(r'[^a-z]', '', str(appointment_type).lower())
    prices = {'checkup': 200, 'emergency': 1000, 'surgery': 5000, 'followup': 150, 'consultation': 250}
    discounts = {'premium': .50, 'standard': .30, 'basic': .10, 'none': 0.0}
    if kind not in prices:
        raise ValueError('Unknown appointment type; a bill was not created.')
    level = str(insurance_level or 'none').strip().lower()
    if level not in discounts:
        raise ValueError('Unknown insurance level; a bill was not created.')
    return round(prices[kind] * (1 - discounts[level]), 2)

def finish_appointment(appointment, insurance_level='none'):
    """Create one demo bill per appointment, then remove it from active appointments."""
    appointments = read_table('appointments.csv')
    bills = read_table('bills.csv')
    existing = bills[(bills['appointment_id'] == appointment.appointmentID) & (bills['patient_id'] == appointment.patientID)]
    if existing.empty:
        if appointment.appointmentID not in appointments['appointment_id'].values:
            raise ValueError('Appointment no longer exists.')
        bill = Bill(str(uuid.uuid4()), appointment.patientID, appointment.appointmentID,
                    calculate_bill(appointment.type, insurance_level))
        save_bills(bill)
    else:
        row = existing.iloc[0]
        bill = Bill(row['bill_id'], int(row['patient_id']), int(row['appointment_id']),
                    float(row['amount']), row['status'].lower() == 'paid')
    write_table(appointments[appointments['appointment_id'] != appointment.appointmentID], 'appointments.csv')
    return bill
