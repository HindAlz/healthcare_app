from storage import read_table, write_table, next_numeric_id
import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime, date, time
from models import Patient, MedicalStaff, Appointment, Bill
APPOINTMENTS_FILE = 'data/appointments.csv'
MEDICAL_HISTORY_FILE = 'data/medical_history.csv'
BILLING_FILE = 'data/bills.csv'
USERS_FILE = 'data/users.csv'
import pandas as pd
from typing import Union, List
from models import Bill

def save_bills_to_csv(bills):
    from services import save_bills
    save_bills(bills)

def save_appointments_to_csv(appointments: list):
    data = [{'appointment_id': a.appointmentID, 'date': a.date.split(' ')[0], 'time': a.date.split(' ')[1], 'patient_id': a.patientID, 'staff_id': a.staffID, 'type': a.type, 'meeting_link': a.info} for a in appointments]
    write_table(pd.DataFrame(data), 'data/appointments.csv')

def load_user_objects():
    df = read_table('data/users.csv')
    user_objects = {}
    for _, row in df.iterrows():
        user_id = row['user_id']
        name = row['name']
        personal_info = {'email': row.get('email'), 'birthday': row.get('birthday'), 'username': row.get('username'), 'specialization': row.get('specialization', ''), 'insurance_level': row.get('insurance_level', 'none')}
        if row['role'] == 'Patient':
            user_objects[user_id] = Patient(user_id, name, personal_info)
        elif row['role'] == 'Staff':
            user_objects[user_id] = MedicalStaff(user_id, name, personal_info, schedule=row.get('schedule', ''), position=row.get('position', ''))
    return user_objects

def load_appointment_objects():
    df = read_table('data/appointments.csv')
    appointments = []
    for _, row in df.iterrows():
        appt = Appointment(appointmentID=row['appointment_id'], date=f"{row['date']} {row['time']}", patientID=row['patient_id'], staffID=row['staff_id'], info=row['meeting_link'], type=row['type'])
        appointments.append(appt)
    return appointments
APPOINTMENTS_FILE = 'data/appointments.csv'
USERS_FILE = 'data/users.csv'
LOGS_FILE = 'data/logs.csv'
import pandas as pd
LOGS_FILE = 'data/logs.csv'

def load_logs():
    try:
        df = read_table(LOGS_FILE)
        df['patient_id'] = df['patient_id'].astype(int)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['patient_id', 'date', 'summary', 'details'])

def save_log_to_file(patient_id, date, summary, details):
    df = load_logs()
    new_entry = pd.DataFrame([{'patient_id': patient_id, 'date': date, 'summary': summary, 'details': details}])
    df = pd.concat([df, new_entry], ignore_index=True)
    write_table(df, LOGS_FILE)

def staff_dashboard():
    if 'staff_page' not in st.session_state:
        st.session_state.staff_page = 'Dashboard'
    match st.session_state.staff_page:
        case 'Dashboard':
            render_staff_home()
        case 'Patients':
            patient_management()
        case 'Schedule':
            appointment_schedule()
        case 'patient_details':
            patient_details()
        case 'add_log':
            add_log()
        case 'log_details':
            log_details()
        case 'end_appointment':
            end_appointment(st.session_state.selected_appointment)

def render_staff_home():
    st.title('Staff Dashboard')
    col1, col2 = st.columns(2)
    if col1.button('🗓️ Appointment Schedule'):
        st.session_state.staff_page = 'Schedule'
        st.rerun()
    if col2.button('👨\u200d⚕️ Patient Management'):
        st.session_state.staff_page = 'Patients'
        st.rerun()

def patient_management():
    st.title('Patient Management')
    if st.button('← Back to Dashboard'):
        st.session_state.staff_page = 'Dashboard'
        st.rerun()
    users = load_user_objects()
    patients = [u for u in users.values() if isinstance(u, Patient)]
    if not patients:
        st.warning('No patients found.')
        return
    search = st.text_input('🔍 Search by name or ID:')
    if search:
        filtered = [p for p in patients if search.lower() in p.name.lower() or str(p.patientID) == search]
    else:
        filtered = patients
    df = pd.DataFrame([{'user_id': p.patientID, 'name': p.name, 'birthday': p.personalInfo.get('birthday'), 'email': p.personalInfo.get('email')} for p in filtered])
    st.dataframe(df)
    ids = [p.patientID for p in filtered]
    selected_id = st.selectbox('Select a patient', ids)
    if selected_id and st.button('Show Info'):
        st.session_state.selected_patient_id = selected_id
        st.session_state.staff_page = 'patient_details'
        st.rerun()

def patient_details():
    user_map = load_user_objects()
    patient = user_map.get(st.session_state.selected_patient_id)
    if not isinstance(patient, Patient):
        st.error('Patient not found.')
        return
    st.title(f'Patient Profile: {patient.name}')
    if st.button('← Back'):
        st.session_state.staff_page = 'Patients'
        st.rerun()
    if st.button('➕ Add Log'):
        st.session_state.staff_page = 'add_log'
        st.session_state.current_patient_id = patient.patientID
        st.rerun()
    st.caption('Synthetic patient profile')
    st.markdown(f"**Email:** {patient.personalInfo.get('email')}")
    st.markdown(f"**Birthday:** {patient.personalInfo.get('birthday')}")
    logs = [l for l in load_logs().to_dict('records') if l['patient_id'] == patient.patientID]
    if logs:
        st.subheader('📄 Visit Logs')
        st.dataframe(pd.DataFrame(logs)[['date', 'summary']])
        selected_log = st.selectbox('Select a log', range(len(logs)), format_func=lambda i: logs[i]['summary'])
        if st.button('➡️ Show Full Log Details'):
            st.session_state.selected_log_index = selected_log
            st.session_state.staff_page = 'log_details'
            st.rerun()
    else:
        st.info('No logs for this patient.')

def add_log():
    st.title('Add New Log')
    if st.button('← Back to Patient'):
        st.session_state.staff_page = 'patient_details'
        st.rerun()
    pid = st.session_state.get('current_patient_id')
    date_val = st.date_input('Date')
    summary = st.text_input('Summary')
    details = st.text_area('Detailed Notes')
    if st.button('Save Log'):
        if summary and details:
            save_log_to_file(pid, str(date_val), summary, details)
            st.success('Log saved.')
            st.session_state.staff_page = 'patient_details'
            st.rerun()
        else:
            st.warning('All fields required.')

def log_details():
    pid = st.session_state.get('selected_patient_id')
    index = st.session_state.get('selected_log_index')
    logs = [row for row in load_logs().to_dict('records') if row['patient_id'] == pid]
    if not isinstance(index, int) or not 0 <= index < len(logs):
        st.warning('Log not found.')
        return
    log = logs[index]
    if st.button('Back to Patient Details'):
        st.session_state.staff_page = 'patient_details'
        st.rerun()
    st.title('Log Details')
    st.write(f"Date: {log['date']}")
    st.write(f"Summary: {log['summary']}")
    st.write(log['details'])
    key = os.environ.get('OPENAI_API_KEY')
    model = os.environ.get('OPENAI_MODEL')
    st.caption('Optional AI demo: sends the displayed summary and notes to OpenAI when requested.')
    synthetic = st.checkbox('This record contains synthetic demo data.')
    if not key or not model:
        st.info('AI demo is disabled. Set OPENAI_API_KEY and OPENAI_MODEL locally to enable it.')
    if st.button('Generate demo summary', disabled=not (key and model and synthetic)):
        try:
            from openai import OpenAI
            with st.spinner('Generating summary...'):
                response = OpenAI(api_key=key).chat.completions.create(model=model, messages=[{'role': 'system', 'content': 'Summarize this fictional healthcare software demo record. Do not diagnose or recommend treatment. Do not invent facts.'}, {'role': 'user', 'content': f"Summary: {log['summary']}. Notes: {log['details']}"}])
            st.info(response.choices[0].message.content or 'No summary returned.')
        except ImportError:
            st.error('Install requirements-ai.txt to use the optional AI demo.')
        except Exception:
            st.error('The AI request failed. Check your local key, model access, and connection.')
import streamlit as st
from models import MedicalStaff, Appointment

def appointment_schedule():
    st.title('Appointment Schedule')
    if st.button('← Back to Dashboard'):
        st.session_state.staff_page = 'Dashboard'
        st.rerun()
    user = st.session_state.get('user')
    if not isinstance(user, MedicalStaff):
        st.error('Access Denied: Staff only.')
        return
    staff: MedicalStaff = user
    appointments = load_appointment_objects()
    staff_appts = [a for a in appointments if a.staffID == staff.staffID]
    if not staff_appts:
        st.write('No appointments.')
        return
    for appt in staff_appts:
        with st.expander(f'Appointment {appt.appointmentID}'):
            st.write(f'📅 Date: **{appt.date}**')
            st.write(f'🧑 Patient ID: **{appt.patientID}**')
            st.write(f'📄 Type: **{appt.type}**')
            st.write(f'Meeting link: {appt.info or "Not provided"}')
            if st.button('🧾 End & Bill', key=f'end_{appt.appointmentID}'):
                st.session_state.selected_appointment = appt
                st.session_state.staff_page = 'end_appointment'
                st.rerun()

def calculate_bill(appointment_type, insurance_level='none'):
    from services import calculate_bill as calculate
    return calculate(appointment_type, insurance_level)

def end_appointment(appt):
    from services import finish_appointment
    if appt.staffID != st.session_state.user.staffID:
        st.error('This appointment is assigned to another staff member.')
        return
    st.subheader('End Appointment')
    patient = load_user_objects().get(appt.patientID)
    insurance = patient.personalInfo.get('insurance_level') or 'none' if patient else 'none'
    try:
        amount = calculate_bill(appt.type, insurance)
    except ValueError as exc:
        st.error(str(exc))
        return
    st.write(f'Demo bill: AED {amount:.2f}')
    if st.button('Confirm & Save Bill'):
        try:
            finish_appointment(appt, insurance)
        except ValueError as exc:
            st.error(str(exc))
            return
        st.success('Bill saved and appointment removed from the active schedule.')
        st.session_state.staff_page = 'Schedule'
        st.rerun()
