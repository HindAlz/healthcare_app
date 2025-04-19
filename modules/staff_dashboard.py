import streamlit as st
import pandas as pd
import os
import streamlit as st
import pandas as pd
import os

# Assuming users.csv and logs are in your data folder
USERS_FILE = os.path.join("data", "users.csv")
import streamlit as st
import pandas as pd
import os

# Assuming users.csv and logs are in your data folder
USERS_FILE = os.path.join("data", "users.csv")

# Patient Management Page
def patient_management():
    st.title("Patient Management")

    try:
        # Load patient data
        df = pd.read_csv(USERS_FILE)
        patients = df[df["role"] == "Patient"]
    except Exception as e:
        st.error(f"Error loading patient data: {e}")
        return

    if patients.empty:
        st.warning("No patients found.")
        return

    # Search functionality for patients - placed above the table
    search = st.text_input("🔍 Search patient by name or ID:")
    if search:
        filtered = patients[
            patients["name"].str.contains(search, case=False, na=False) |
            patients["user_id"].astype(str).str.contains(search)
        ]
    else:
        filtered = patients

    # Displaying patients in a table
    st.subheader("Patient List")
    patients_table = filtered[["user_id", "name", "birthday", "email"]]
    st.dataframe(patients_table)

    # Allow patient selection by clicking on their row
    selected_patient_id = None
    patient_ids = filtered["user_id"].tolist()
    selected_patient_id = st.selectbox("Select a patient to view their logs", patient_ids)

    # If a patient is selected, show their info and logs on a separate page
    if selected_patient_id:
        if st.button(f"Show Info for Patient ID {selected_patient_id}"):
            st.session_state.selected_patient_id = selected_patient_id
            st.session_state.staff_page = "patient_details"
            st.rerun()

# Patient Details Page
# Patient Details Page
def patient_details():
    # Button to return to the patient list
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("← Back", key="back_from_patient"):
            st.session_state.staff_page = "Dashboard"

    patient_id = st.session_state.get("selected_patient_id")

    # Load patient data
    df = pd.read_csv(USERS_FILE)
    patient = df[df["user_id"] == patient_id].iloc[0]

    # Display the patient's profile
    st.title(f"Patient Profile: {patient['name']}")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("https://via.placeholder.com/150", width=150, caption="Patient Image")
    with col2:
        st.markdown(f"**Name:** {patient['name']}")
        st.markdown(f"**Birthday:** {patient['birthday']}")
        st.markdown(f"**Email:** {patient['email'] or 'N/A'}")
        st.markdown(f"**Phone Number:** Not provided")

    # Placeholder logs for demonstration
    patient_logs = {
        1: [
            {"date": "2025-04-01", "summary": "Cough and fever"},
            {"date": "2025-04-10", "summary": "Mild improvement on follow-up"}
        ],
        4: [
            {"date": "2025-04-03", "summary": "High blood sugar"},
            {"date": "2025-04-12", "summary": "Routine check-up"}
        ]
    }
    logs = patient_logs.get(patient_id, [])

    if logs:
        st.subheader("📄 Visit Logs")
        log_summaries = [{"Date": log["date"], "Summary": log["summary"]} for log in logs]
        log_df = pd.DataFrame(log_summaries)

        # Display log summaries in a table
        st.dataframe(log_df)

        # Show log details only when "Show Full Log" is clicked
        selected_log_index = st.selectbox("Select a log to view its details", range(len(logs)), format_func=lambda idx: f"{logs[idx]['date']} - {logs[idx]['summary']}")

        if selected_log_index is not None:
            if st.button("➡️ Show Full Log Details"):
                # Update the session state with selected log index
                st.session_state.selected_log_index = selected_log_index
                # Change the page to show log details
                st.session_state.staff_page = "log_details"
                st.rerun()

    else:
        st.info("No logs available for this patient.")



def log_details():
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("← Back", key="back_from_log"):
            st.session_state.staff_page = "patient_details"
    patient_id = st.session_state.get("selected_patient_id")
    log_index = st.session_state.get("selected_log_index")

    if patient_id is None or log_index is None:
        st.warning("No log selected.")
        return

    # Patient data
    df = pd.read_csv(USERS_FILE)
    patient = df[df["user_id"] == patient_id].iloc[0]

    # Get the log entry
    patient_logs = {
        1: [
            {"date": "2025-04-01", "summary": "Cough and fever", "details": "The patient reported a 3-day history of cough and fever."},
            {"date": "2025-04-10", "summary": "Follow-up visit, mild improvement", "details": "Symptoms have reduced, mild fever persists."}
        ],
        4: [
            {"date": "2025-04-03", "summary": "High blood sugar", "details": "Blood sugar levels were elevated, monitored during visit."},
            {"date": "2025-04-12", "summary": "Routine check-up", "details": "No major issues found during check-up."}
        ]
    }
    logs = patient_logs.get(patient_id, [])
    if log_index >= len(logs):
        st.error("Log not found.")
        return

    log = logs[log_index]

    st.title(f"🗂️ Detailed Log for {patient['name']}")
    st.markdown(f"**Date:** {log['date']}")
    st.markdown(f"**Summary:** {log['summary']}")
    st.markdown(f"**Detailed Notes:**\n{log['details']}")
    st.markdown("**Technical Info:**\nBlood Pressure: 120/80 mmHg, Temperature: 37.8°C, Oxygen Saturation: 97%")

    st.divider()
    st.markdown("### 🧠 AI Diagnosis Suggestion")
    st.success("AI Suggests: Possible viral infection. Recommend a CBC test and hydration.")




# Sidebar Navigation (optional if you want a sidebar)
def sidebar_navigation():
    st.sidebar.title("Navigation")
    options = ["Dashboard", "Patients", "Schedule"]

    current_page = st.session_state.get("staff_page", "Dashboard")
    sidebar_index = options.index(current_page) if current_page in options else 0

    selected = st.sidebar.radio("Go to", options, index=sidebar_index)

    if selected != current_page and current_page in options:
        st.session_state.staff_page = selected
        st.rerun()

# Staff Homepage (Dashboard)
def render_staff_home():
    st.title("Staff Dashboard")
    st.write("Welcome to your dashboard. Use the buttons below or the sidebar to navigate.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗓️ Appointment Schedule"):
            st.session_state.staff_page = "Schedule"
            st.rerun()

    with col2:
        if st.button("👨‍⚕️ Patient Management"):
            st.session_state.staff_page = "Patients"
            st.rerun()

# Appointment Schedule Page
def appointment_schedule():
    st.title("Appointment Schedule")

    user = st.session_state.user

    if user["role"] != "Staff":
        st.error("Access Denied: You are not authorized to view this page.")
        return

    st.sidebar.subheader(f"Work Hours: {user['schedule']}")
    st.sidebar.text(f"Position: {user['position']}")

    appointments = load_appointments()
    staff_appointments = appointments[appointments['staff_id'] == user['user_id']]

    if staff_appointments.empty:
        st.write("No upcoming appointments.")
    else:
        st.subheader("Upcoming Appointments")
        for _, appt in staff_appointments.iterrows():
            with st.expander(f"Appointment {appt['appointment_id']}"):
                st.write(f"📅 Date: **{appt['date']}**")
                st.write(f"⏰ Time: **{appt['time']}**")
                st.write(f"🧑 Patient ID: {appt['patient_id']}")
                st.write(f"📄 Type: {appt['type']}")
                st.markdown(f"[🔗 Join Meeting]({appt['meeting_link']})", unsafe_allow_html=True)

                if st.button(f"Modify Appointment {appt['appointment_id']}"):
                    st.session_state.modify_id = appt['appointment_id']
                    st.session_state.staff_page = "Modify"
                    st.rerun()

# Staff Dashboard Entry Point
def staff_dashboard():
    if "staff_page" not in st.session_state:
        st.session_state["staff_page"] = "Dashboard"

    # Sidebar navigation
    sidebar_navigation()

    # Page navigation based on staff_page only
    if st.session_state.staff_page == "Patients":
        patient_management()
    elif st.session_state.staff_page == "Schedule":
        appointment_schedule()
    elif st.session_state.staff_page == "Modify":
        modify_appointment()
    elif st.session_state.staff_page == "patient_details":
        patient_details()
    elif st.session_state.staff_page == "log_details":
        log_details()
    else:
        render_staff_home()


APPOINTMENTS_FILE = os.path.join("data", "appointments.csv")
def appointment_schedule():
    st.title("Appointment Schedule")

    user = st.session_state.user

    if user["role"] != "Staff":
        st.error("Access Denied: You are not authorized to view this page.")
        return

    st.sidebar.subheader(f"Work Hours: {user['schedule']}")
    st.sidebar.text(f"Position: {user['position']}")

    appointments = load_appointments()
    staff_appointments = appointments[appointments['staff_id'] == user['user_id']]

    if staff_appointments.empty:
        st.write("No upcoming appointments.")
    else:
        st.subheader("Upcoming Appointments")
        for _, appt in staff_appointments.iterrows():
            with st.expander(f"Appointment {appt['appointment_id']}"):
                st.write(f"📅 Date: **{appt['date']}**")
                st.write(f"⏰ Time: **{appt['time']}**")
                st.write(f"🧑 Patient ID: {appt['patient_id']}")
                st.write(f"📄 Type: {appt['type']}")
                st.markdown(f"[🔗 Join Meeting]({appt['meeting_link']})", unsafe_allow_html=True)

                if st.button(f"Modify Appointment {appt['appointment_id']}"):
                    st.session_state.modify_id = appt['appointment_id']
                    st.session_state.staff_page = "Modify"
                    st.rerun()

# Load appointments
def load_appointments():
    try:
        return pd.read_csv(APPOINTMENTS_FILE)
    except Exception as e:
        st.error(f"Failed to load appointments: {e}")
        return pd.DataFrame(columns=["appointment_id", "date", "time", "patient_id", "staff_id", "type", "meeting_link"])

# Load all users and filter patients
def load_patients():
    try:
        df = pd.read_csv(USERS_FILE)
        return df[df["role"] == "Patient"]
    except Exception as e:
        st.error(f"Error loading patient data: {e}")
        return pd.DataFrame()

# Patient logs (placeholder)
patient_logs = {
    1: [{"date": "2025-04-01", "summary": "Cough and fever"},
        {"date": "2025-04-10", "summary": "Follow-up visit, mild improvement"}],
    4: [{"date": "2025-04-03", "summary": "High blood sugar"},
        {"date": "2025-04-12", "summary": "Routine check-up"}]
}
# Staff Homepage

# Modify Appointment Page
def modify_appointment():
    st.title("📝 Modify Appointment")

    appointments = load_appointments()
    appointment_id = int(st.session_state.get("modify_id", -1))

    if appointment_id == -1 or appointment_id not in appointments["appointment_id"].values:
        st.error("❌ Invalid appointment selected.")
        return

    appointment = appointments[appointments["appointment_id"] == appointment_id].iloc[0]

    st.markdown(f"### Editing Appointment ID: `{appointment_id}`")

    # Editable fields
    new_date = st.date_input("📅 Date", pd.to_datetime(appointment["date"]))
    new_time = st.time_input("⏰ Time", pd.to_datetime(appointment["time"]).time())
    new_type = st.selectbox(
        "📄 Appointment Type",
        ["Consultation", "Checkup", "Emergency", "Follow-up"],
        index=["Consultation", "Checkup", "Emergency", "Follow-up"].index(appointment["type"])
    )
    new_link = st.text_input("🔗 Meeting Link", appointment["meeting_link"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Changes"):
            appointments.loc[appointments["appointment_id"] == appointment_id, ["date", "time", "type", "meeting_link"]] = [
                str(new_date), str(new_time), new_type, new_link
            ]
            appointments.to_csv(APPOINTMENTS_FILE, index=False)
            st.success("✅ Appointment updated successfully.")
            st.session_state.staff_page = "Schedule"
            st.rerun()

    with col2:
        if st.button("↩️ Cancel"):
            st.session_state.staff_page = "Schedule"
            st.rerun()

