import streamlit as st
import pandas as pd
from datetime import datetime

# Example ER Staff appointments (you can replace this with real data)
appointments = {
    "appointment_id": [1, 2, 3],
    "patient_name": ["John Doe", "Jane Smith", "Jim Brown"],
    "doctor_name": ["Dr. White", "Dr. Black", "Dr. Green"],
    "appointment_time": [datetime(2025, 4, 20, 9, 0), datetime(2025, 4, 20, 10, 0), datetime(2025, 4, 20, 11, 0)],
    "appointment_type": ["Emergency", "Emergency", "Non-Emergency"]
}

# Convert to a DataFrame
df_appointments = pd.DataFrame(appointments)

# ER Staff Dashboard
def er_dashboard():
    st.title("ER Staff Dashboard")

    # Load user and check if role is ER Staff
    user = st.session_state.user
    if user["role"] != "ER Staff":
        st.error("Access Denied: You are not authorized to view this page.")
        return

    # ER Staff work hours (dummy data for now)
    st.sidebar.subheader("ER Staff Work Hours")
    st.sidebar.write("Work Hours: 9:00 AM - 5:00 PM (Mon to Fri)")  # This is editable by the admin

    # View Appointments
    st.subheader("Upcoming Appointments")
    st.write(df_appointments[["appointment_id", "patient_name", "doctor_name", "appointment_time", "appointment_type"]])

    # Join Virtual Meetings
    st.subheader("Virtual Meeting Links")
    meeting_link = st.text_input("Enter Appointment ID to Join Meeting", "")
    if meeting_link:
        st.write(f"Join the virtual meeting for appointment {meeting_link}")
        # You can add your logic for joining the meeting here (e.g., redirect to a URL)

    # View Patient Medical History (Limited access)
    patient_id = st.text_input("Enter Patient ID to View Medical History", "")
    if patient_id:
        st.write(f"Viewing limited medical history for Patient ID {patient_id}")
        # Dummy data for the medical history
        medical_history = {
            "date": ["2025-04-10", "2025-04-18"],
            "summary": ["Initial ER visit for fever", "Follow-up after ER visit for fever"]
        }
        history_df = pd.DataFrame(medical_history)
        st.write(history_df)

    # Back button
    if st.button("Back to Dashboard"):
        st.session_state.user = None  # Log the user out or redirect to a homepage
        st.rerun()
