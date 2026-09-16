import pandas as pd
import streamlit as st
from storage import read_table

def load_emergencies():
    df = read_table('appointments.csv')
    emergencies = df[df['type'].str.contains('emergency', case=False, na=False, regex=False)].copy()
    # Do not invent severity or incident addresses from appointment records.
    emergencies['severity'] = 'Not recorded'
    emergencies['status'] = 'Unassigned'
    return emergencies

def er_dashboard():
    if getattr(st.session_state.get('user'), 'role', None) != 'ER':
        st.error('Access denied: ER accounts only.')
        return
    st.title('Emergency Appointments — Demo')
    st.caption('This view does not triage patients or dispatch emergency services.')
    df = load_emergencies()
    if df.empty:
        st.info('No emergency appointments recorded.')
        return
    query = st.text_input('Search by patient or appointment ID').strip()
    if query:
        df = df[df['patient_id'].astype(str).str.contains(query, regex=False) |
                df['appointment_id'].astype(str).str.contains(query, regex=False)]
    st.dataframe(df[['appointment_id','patient_id','type','date','time','severity','status']], hide_index=True)
