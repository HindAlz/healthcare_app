import streamlit as st
import pandas as pd
import os
import uuid

USERS_FILE = os.path.join("data", "users.csv")
APPOINTMENTS_FILE = os.path.join("data", "appointments.csv")

# Dummy appointments loader
def load_appointments():
    try:
        return pd.read_csv(APPOINTMENTS_FILE)
    except:
        return pd.DataFrame(columns=["appointment_id", "staff_id", "patient_id", "date", "time", "type", "meeting_link"])

# Dummy AI diagnosis function
def generate_diagnosis(details):
    return "AI Suggests: Possible viral infection. Recommend a CBC test and hydration."

# Patient Management Page
def patient_management():
    st.title("Patient Management")
    if st.button("← Back to Dashboard"):
        st.session_state.staff_page = "Dashboard"
        st.rerun()

    try:
        df = pd.read_csv(USERS_FILE)
        patients = df[df["role"] == "Patient"]
    except Exception as e:
        st.error(f"Error loading patient data: {e}")
        return

    if patients.empty:
        st.warning("No patients found.")
        return

    search = st.text_input("🔍 Search patient by name or ID:")
    if search:
        filtered = patients[
            patients["name"].str.contains(search, case=False, na=False) |
            patients["user_id"].astype(str).str.contains(search)
        ]
    else:
        filtered = patients

    st.subheader("Patient List")
    st.dataframe(filtered[["user_id", "name", "birthday", "email"]])

    selected_patient_id = st.selectbox("Select a patient to view their logs", filtered["user_id"].tolist())

    if selected_patient_id and st.button(f"Show Info for Patient ID {selected_patient_id}"):
        st.session_state.selected_patient_id = selected_patient_id
        st.session_state.staff_page = "patient_details"
        st.rerun()

# Patient Details Page
def patient_details():
    patient_id = st.session_state.get("selected_patient_id")
    df = pd.read_csv(USERS_FILE)
    patient = df[df["user_id"] == patient_id].iloc[0]

    st.title(f"Patient Profile: {patient['name']}")
    col1, col2, col3 = st.columns([1, 8, 3])

    with col1:
        if st.button("← Back"):
            # Go back to patient list, not dashboard
            st.session_state.staff_page = "Patients"
            st.rerun()

    with col3:
        if st.button("➕ Add Log"):
            st.session_state.staff_page = "add_log"
            st.session_state.current_patient_id = patient_id
            st.rerun()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://via.placeholder.com/150", width=150)
    with col2:
        st.markdown(f"**Name:** {patient['name']}")
        st.markdown(f"**Birthday:** {patient['birthday']}")
        st.markdown(f"**Email:** {patient['email'] or 'N/A'}")
        st.markdown(f"**Phone Number:** Not provided")

    # Placeholder logs
    logs = st.session_state.get("logs", {}).get(patient_id, [])
    if logs:
        st.subheader("📄 Visit Logs")
        log_df = pd.DataFrame(logs)[["date", "summary"]]
        st.dataframe(log_df)

        selected_log_index = st.selectbox("Select a log to view its details", range(len(logs)),
                                          format_func=lambda idx: f"{logs[idx]['date']} - {logs[idx]['summary']}")
        if st.button("➡️ Show Full Log Details"):
            st.session_state.selected_log_index = selected_log_index
            st.session_state.staff_page = "log_details"
            st.rerun()
    else:
        st.info("No logs available for this patient.")

def log_details():
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("← Back"):
            st.session_state.staff_page = "patient_details"
            st.rerun()

    patient_id = st.session_state.get("selected_patient_id")
    log_index = st.session_state.get("selected_log_index")
    logs = st.session_state.get("logs", {}).get(patient_id, [])

    if patient_id is None or log_index is None or log_index >= len(logs):
        st.warning("Log not found.")
        return

    log = logs[log_index]
    df = pd.read_csv(USERS_FILE)
    patient = df[df["user_id"] == patient_id].iloc[0]

    st.title(f"🗂️ Detailed Log for {patient['name']}")
    st.markdown(f"**Date:** {log['date']}")
    st.markdown(f"**Summary:** {log['summary']}")
    st.markdown(f"**Detailed Notes:**\n{log['details']}")
    st.divider()
    st.markdown("### 🧠 AI Diagnosis Suggestion")
    st.success(log.get("ai_diagnosis", "N/A"))

def add_log():
    st.title("Add New Log")

    if st.button("← Back to Patient"):
        st.session_state.staff_page = "patient_details"
        st.rerun()

    patient_id = st.session_state.get("current_patient_id")
    if not patient_id:
        st.error("No patient selected.")
        return

    log_date = st.date_input("Log Date")
    summary = st.text_input("Summary")
    details = st.text_area("Detailed Notes")

    if st.button("Save Log"):
        if summary and details:
            new_log = {
                "date": str(log_date),
                "summary": summary,
                "details": details,
                "ai_diagnosis": generate_diagnosis(details)
            }
            logs = st.session_state.get("logs", {})
            logs.setdefault(patient_id, []).append(new_log)
            st.session_state.logs = logs
            st.success("Log saved successfully.")
            st.session_state.staff_page = "patient_details"
            st.rerun()
        else:
            st.warning("Please fill in all fields.")

def appointment_schedule():
    st.title("Appointment Schedule")

    user = st.session_state.get("user", {"user_id": 1, "role": "Staff", "schedule": "9AM–5PM", "position": "General Physician"})

    if user["role"] != "Staff":
        st.error("Access Denied")
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


def sidebar_navigation():
    st.sidebar.title("Navigation")
    options = ["Dashboard", "Patients", "Schedule"]

    if "staff_page" not in st.session_state:
        st.session_state.staff_page = "Dashboard"

    current_page = st.session_state.staff_page
    selected = st.sidebar.radio("Go to", options, index=options.index(current_page) if current_page in options else 0)

    # Only change page if user actually clicks a new one
    if selected != current_page and st.session_state.staff_page in options:
        st.session_state.staff_page = selected
        st.rerun()


def render_staff_home():
    st.title("Staff Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗓️ Appointment Schedule"):
            st.session_state.staff_page = "Schedule"
            st.rerun()
    with col2:
        if st.button("👨‍⚕️ Patient Management"):
            st.session_state.staff_page = "Patients"
            st.rerun()
def staff_dashboard():
    # Important: Set default BEFORE any other logic
    if "staff_page" not in st.session_state:
        st.session_state["staff_page"] = "Dashboard"

    st.sidebar.write("DEBUG: staff_page =", st.session_state.get("staff_page"))

    sidebar_navigation()  # Don't override the page unless user selects a new one

    match st.session_state.staff_page:
        case "Patients":
            patient_management()
        case "Schedule":
            appointment_schedule()
        case "patient_details":
            patient_details()
        case "log_details":
            log_details()
        case "add_log":
            add_log()
        case _:
            render_staff_home()

# Run the dashboard
staff_dashboard()
