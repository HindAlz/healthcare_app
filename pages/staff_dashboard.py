import streamlit as st
import pandas as pd

# File paths
APPOINTMENTS_FILE = "data/appointments.csv"


# Load appointments
def load_appointments():
    try:
        return pd.read_csv(APPOINTMENTS_FILE)
    except Exception:
        return pd.DataFrame(
            columns=["appointment_id", "date", "time", "patient_id", "staff_id", "type", "meeting_link"])


# Staff dashboard
def staff_dashboard():
    st.title("Staff Dashboard")

    # Load user and check if the role is staff
    user = st.session_state.user
    if user["role"] != "Staff":
        st.error("Access Denied: You are not authorized to view this page.")
        return

    # Staff work hours
    st.sidebar.subheader(f"Work Hours: {user['schedule']}")
    st.sidebar.text(f"Position: {user['position']}")

    # Display staff appointments
    appointments = load_appointments()
    staff_appointments = appointments[appointments['staff_id'] == user['user_id']]

    if staff_appointments.empty:
        st.write("No upcoming appointments.")
    else:
        st.subheader("Upcoming Appointments")
        for index, appointment in staff_appointments.iterrows():
            st.write(f"Appointment ID: {appointment['appointment_id']}")
            st.write(f"Date: {appointment['date']}, Time: {appointment['time']}")
            st.write(f"Patient ID: {appointment['patient_id']}")
            st.write(f"Type: {appointment['type']}")
            st.write(f"Meeting Link: [Join Meeting]({appointment['meeting_link']})")
            if st.button(f"Modify Appointment {appointment['appointment_id']}"):
                modify_appointment(appointment['appointment_id'])

    # Return button to go back to the main dashboard
    if st.button("Return to Main Dashboard"):
        st.session_state.user = None  # Clear user session
        st.rerun()


def modify_appointment(appointment_id):
    # Modify appointment functionality
    appointments = load_appointments()
    appointment = appointments[appointments["appointment_id"] == appointment_id].iloc[0]

    st.subheader(f"Modify Appointment {appointment_id}")
    date = st.date_input("Date", pd.to_datetime(appointment["date"]))
    time = st.time_input("Time", pd.to_datetime(appointment["time"]).time())
    appointment_type = st.selectbox("Type", ["Consultation", "Checkup", "Emergency", "Follow-up"],
                                    index=["Consultation", "Checkup", "Emergency", "Follow-up"].index(
                                        appointment["type"]))
    meeting_link = st.text_input("Meeting Link", appointment["meeting_link"])

    if st.button("Save Changes"):
        appointments.loc[appointments["appointment_id"] == appointment_id, ["date", "time", "type", "meeting_link"]] = [
            date, time, appointment_type, meeting_link]
        appointments.to_csv(APPOINTMENTS_FILE, index=False)
        st.success("Appointment modified successfully!")
