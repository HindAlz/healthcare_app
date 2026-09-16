from auth import hash_password
from storage import read_table, write_table, next_numeric_id
import streamlit as st
import pandas as pd
from datetime import datetime
import os
APPOINTMENTS_FILE = 'data/appointments.csv'
MEDICAL_HISTORY_FILE = 'data/medical_history.csv'
BILLING_FILE = 'data/bills.csv'
USERS_FILE = 'data/users.csv'
import pandas as pd

def load_medications():
    return read_table('medications.csv')

def load_devices():
    return read_table('devices.csv')

def load_consumables():
    return read_table('consumables.csv')

def resource_management():
    if st.button('Return to Dashboard - Staff'):
        st.session_state.selected_page = None
        st.rerun()
    st.header('Resource Management')
    option = st.selectbox('Select Resource', ['Medications', 'Devices', 'Consumables'], key='resource_select')
    today = datetime.today().date()
    if option == 'Medications':
        meds = load_medications()
        if isinstance(meds, list):
            meds = pd.DataFrame(meds)
        show_add_new_form('Medication', meds, 'data/medications.csv', 'MED', fields=[('name', 'text'), ('stock', 'number'), ('expiry', 'date'), ('low_stock', 'number')])
        
        st.dataframe(meds)
        if meds.empty:
            st.info('No resources yet. Add the first item above.')
            return
        for _, row in meds.iterrows():
            if 'low_stock' not in row:
                st.error("Column 'low_stock' is missing in medication data.")
            else:
                if row['stock'] < row['low_stock']:
                    st.warning(f"Low stock for {row['med_id']}")
                expiry = datetime.strptime(row['expiry'], '%Y-%m-%d').date()
                if (expiry - today).days < 30:
                    st.error(f"Medication {row['med_id']} nearing expiry on {row['expiry']}")
        selected = st.selectbox('Select medication to restock', meds['med_id'].tolist(), key='restock_med_select')
        if st.button('Restock Selected Medication', key='restock_med_btn'):
            meds.loc[meds['med_id'] == selected, 'stock'] = meds.loc[meds['med_id'] == selected, 'low_stock']
            write_table(meds, 'data/medications.csv')
            st.success(f'{selected} restocked to threshold.')
            st.rerun()
    elif option == 'Devices':
        devices = load_devices()
        if isinstance(devices, list):
            devices = pd.DataFrame(devices)
        show_add_new_form('Device', devices, 'data/devices.csv', 'DEV', fields=[('name', 'text'), ('available', 'number'), ('next_maintenance', 'date'), ('low_available', 'number')])
        st.dataframe(devices)
        if devices.empty:
            st.info('No resources yet. Add the first item above.')
            return
        for _, row in devices.iterrows():
            if row['available'] < row['low_available']:
                st.warning(f"Low availability for {row['device_id']}")
            next_maint = datetime.strptime(row['next_maintenance'], '%Y-%m-%d').date()
            if (next_maint - today).days < 30:
                st.error(f"Device {row['device_id']} needs maintenance soon ({row['next_maintenance']})")
        selected = st.selectbox('Select device to restock', devices['device_id'].tolist(), key='restock_device_select')
        if st.button('Restock Selected Device', key='restock_device_btn'):
            devices.loc[devices['device_id'] == selected, 'available'] = devices.loc[devices['device_id'] == selected, 'low_available']
            write_table(devices, 'data/devices.csv')
            st.success(f'{selected} restocked to threshold.')
            st.rerun()
    elif option == 'Consumables':
        cons = load_consumables()
        if isinstance(cons, list):
            cons = pd.DataFrame(cons)
        show_add_new_form('Consumable', cons, 'data/consumables.csv', 'CON', fields=[('name', 'text'), ('stock', 'number'), ('expiry', 'date'), ('low_stock', 'number')])
        st.dataframe(cons)
        if cons.empty:
            st.info('No resources yet. Add the first item above.')
            return
        for _, row in cons.iterrows():
            if row['stock'] < row['low_stock']:
                st.warning(f"Low stock for {row['consumable_id']}")
            expiry = datetime.strptime(row['expiry'], '%Y-%m-%d').date()
            if (expiry - today).days < 30:
                st.error(f"Consumable {row['consumable_id']} expiring soon ({row['expiry']})")
        selected = st.selectbox('Select consumable to restock', cons['consumable_id'].tolist(), key='restock_cons_select')
        if st.button('Restock Selected Consumable', key='restock_cons_btn'):
            cons.loc[cons['consumable_id'] == selected, 'stock'] = cons.loc[cons['consumable_id'] == selected, 'low_stock']
            write_table(cons, 'data/consumables.csv')
            st.success(f'{selected} restocked to threshold.')
            st.rerun()

def show_add_new_form(resource_type, resources, filename, prefix, fields):
    st.subheader(f'Add {resource_type}')
    with st.form(f'{resource_type}_form'):
        values = {}
        for name, kind in fields:
            if kind == 'text':
                values[name] = st.text_input(name)
            elif kind in ('int', 'number'):
                values[name] = st.number_input(name, min_value=0, step=1)
            elif kind == 'date':
                values[name] = st.date_input(name).isoformat()
        submitted = st.form_submit_button(f'Add {resource_type}')
    if submitted:
        if not values.get('name', '').strip():
            st.error('Enter a resource name.')
            return
        id_column = {'MED': 'med_id', 'DEV': 'device_id', 'CON': 'consumable_id'}[prefix]
        existing = set(resources[id_column].astype(str))
        number = 1
        while f'{prefix}{number:03d}' in existing:
            number += 1
        values[id_column] = f'{prefix}{number:03d}'
        write_table(pd.concat([resources, pd.DataFrame([values])], ignore_index=True), filename)
        st.success(f'{resource_type} added.')
        st.rerun()

def save_resources(resources, filename):
    df = pd.DataFrame(resources)
    write_table(df, filename)

def load_user_objects():
    df = read_table(USERS_FILE)
    user_objects = {}
    for _, row in df.iterrows():
        user_id = row['user_id']
        name = row['name']
        personal_info = {'email': row.get('email'), 'birthday': row.get('birthday'), 'username': row.get('username'), 'specialization': row.get('specialization', '')}
        if row['role'] == 'Patient':
            user_objects[user_id] = {'role': 'Patient', 'name': name, 'personal_info': personal_info}
        elif row['role'] == 'Staff':
            user_objects[user_id] = {'role': 'Staff', 'name': name, 'personal_info': personal_info, 'schedule': row.get('schedule', ''), 'position': row.get('position', '')}
    return user_objects

def load_appointment_objects():
    df = read_table(APPOINTMENTS_FILE)
    appointments = []
    for _, row in df.iterrows():
        appt = {'appointmentID': row['appointment_id'], 'date': f"{row['date']} {row['time']}", 'patientID': row['patient_id'], 'staffID': row['staff_id'], 'info': row['meeting_link'], 'type': row['type']}
        appointments.append(appt)
    return appointments

def load_medical_histories(user_map):
    df = read_table(MEDICAL_HISTORY_FILE)
    for _, row in df.iterrows():
        patient = user_map.get(row['patient_id'])
        if patient and patient['role'] == 'Patient':
            day, month, year = map(int, row['date'].split('-'))
            if 'history' not in patient:
                patient['history'] = []
            patient['history'].append({'date': f'{day}-{month}-{year}', 'summary': row['summary']})

def load_bill_objects():
    df = read_table(BILLING_FILE)
    bills = []
    for _, row in df.iterrows():
        bill = {'billID': row['bill_id'], 'patientID': row['patient_id'], 'appointmentID': row['appointment_id'], 'amount': row['amount'], 'paid': str(row.get('status', '')).strip().lower() == 'paid'}
        bills.append(bill)
    return bills

def save_users_df(df: pd.DataFrame):
    write_table(df, USERS_FILE)

def load_users_df() -> pd.DataFrame:
    try:
        return read_table(USERS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=['user_id', 'username', 'password', 'role', 'name', 'birthday', 'email', 'position', 'specialization', 'schedule'])

def admin_dashboard():
    st.title('Admin Dashboard')
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = None
    if st.session_state.selected_page is None:
        col1, col2, col3 = st.columns(3)
        if col1.button('Staff Management'):
            st.session_state.selected_page = 'staff_management'
            st.rerun()
        if col2.button('Patient Management'):
            st.session_state.selected_page = 'patient_management'
            st.rerun()
        if col3.button('Resource Management'):
            st.session_state.selected_page = 'resource_management'
            st.rerun()
    if st.session_state.selected_page == 'staff_management':
        staff_management()
    elif st.session_state.selected_page == 'patient_management':
        patient_management()
    elif st.session_state.selected_page == 'resource_management':
        resource_management()

def staff_management():
    if 'show_add_staff_form' not in st.session_state:
        st.session_state.show_add_staff_form = False
    if 'show_staff_info' not in st.session_state:
        st.session_state.show_staff_info = False
    if 'selected_staff_id' not in st.session_state:
        st.session_state.selected_staff_id = None
    if st.button('🔙 Return to Dashboard'):
        st.session_state.selected_page = None
        st.rerun()
    top1, top2 = st.columns([5, 1])
    with top1:
        st.header('Staff Management')
    with top2:
        if st.button('➕ Add New Staff'):
            st.session_state.show_add_staff_form = True
            st.session_state.show_staff_info = False
            st.session_state.selected_staff_id = None
    df = load_users_df()
    staff_df = df[df['role'] == 'Staff']
    search = st.text_input('Search Staff by ID or Name').lower()
    if search:
        staff_filtered = staff_df[staff_df['user_id'].astype(str).str.contains(search, regex=False) | staff_df['name'].str.lower().str.contains(search, regex=False)]
    else:
        staff_filtered = staff_df
    st.dataframe(staff_filtered[['user_id', 'name', 'specialization', 'schedule']], use_container_width=True)
    staff_ids = staff_filtered['user_id'].tolist()
    selected = st.selectbox('Select a Staff ID', staff_ids, key='select_staff_id')
    if st.button('View Info'):
        st.session_state.selected_staff_id = selected
        st.session_state.show_staff_info = True
        st.session_state.show_add_staff_form = False
    if st.session_state.show_staff_info and st.session_state.selected_staff_id:
        staff = staff_df[staff_df['user_id'] == st.session_state.selected_staff_id].iloc[0]
        st.subheader(f"Staff Info: {staff['name']}")
        with st.form('edit_staff_form'):
            name = st.text_input('Name', value=staff['name'])
            specialization = st.text_input('Specialization', value=staff['specialization'])
            schedule = st.text_input('Schedule', value=staff['schedule'])
            email = st.text_input('Email', value=staff['email'])
            submit_edit = st.form_submit_button('💾 Save Changes')
            if submit_edit:
                df.loc[df['user_id'] == staff['user_id'], 'name'] = name
                df.loc[df['user_id'] == staff['user_id'], 'specialization'] = specialization
                df.loc[df['user_id'] == staff['user_id'], 'schedule'] = schedule
                df.loc[df['user_id'] == staff['user_id'], 'email'] = email
                save_users_df(df)
                st.success('✅ Staff info updated.')
                st.session_state.show_staff_info = False
                st.session_state.selected_staff_id = None
                st.rerun()
    if st.session_state.show_add_staff_form:
        st.subheader('Add New Staff')
        with st.form('new_staff_form'):
            new_id = next_numeric_id(df, 'user_id')
            st.caption(f'Assigned user ID: {new_id}')
            username = st.text_input('Username')
            password = st.text_input('Password (at least 12 characters)', type='password')
            name = st.text_input('Name')
            birthday = st.date_input('Birthday')
            email = st.text_input('Email')
            position = st.text_input('Position')
            specialization = st.text_input('Specialization')
            schedule = st.text_input('Schedule')
            submit = st.form_submit_button('➕ Add Staff')
            if submit:
                if not username.strip() or not name.strip() or '@' not in email or len(password) < 12:
                    st.error('Enter a username, name, email, and a password of at least 12 characters.')
                    return
                if username.strip().casefold() in set(df['username'].str.casefold()):
                    st.error('Username already exists.')
                    return
                new_entry = pd.DataFrame([{'user_id': new_id, 'username': username.strip(), 'password': hash_password(password), 'role': 'Staff', 'name': name, 'birthday': birthday.isoformat(), 'email': email, 'position': position, 'specialization': specialization, 'schedule': schedule}])
                df = pd.concat([df, new_entry], ignore_index=True)
                save_users_df(df)
                st.success('✅ New staff added.')
                st.session_state.show_add_staff_form = False
                st.rerun()
import pandas as pd
import streamlit as st

def patient_management():
    if st.button('Return to Dashboard - Staff'):
        st.session_state.selected_page = None
        st.rerun()
    st.header('Patient Management')
    patients = load_users_df()
    appointments = load_appointment_objects()
    bills = load_bill_objects()
    patients = patients[patients['role'] == 'Patient']
    search = st.text_input('Search Patient by ID or Name').lower()
    if search:
        patients_filtered = patients[patients['user_id'].astype(str).str.contains(search, regex=False) | patients['name'].str.lower().str.contains(search, regex=False)]
    else:
        patients_filtered = patients
    st.dataframe(patients_filtered[['user_id', 'name', 'birthday', 'email']], use_container_width=True)
    if not patients_filtered.empty:
        selected_patient_id = st.selectbox('Select a Patient', patients_filtered['user_id'])
        selected_patient_id = str(selected_patient_id)
        patient_bills = [bill for bill in bills if str(bill['patientID']) == selected_patient_id]
        if patient_bills:
            st.subheader("Patient's Bills")
            bill_data = pd.DataFrame(patient_bills)
            st.dataframe(bill_data[['billID', 'appointmentID', 'amount', 'paid']], use_container_width=True)
        else:
            st.write('No bills available for this patient.')
import pandas as pd
if __name__ == '__main__':
    admin_dashboard()
