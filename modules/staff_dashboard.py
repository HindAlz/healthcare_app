import streamlit as st
import pandas as pd
import os
import uuid

# Set your OpenAI API key securely
from openai import OpenAI
client = OpenAI(api_key="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")
LOGS_FILE = os.path.join("data", "logs.csv")
USERS_FILE = os.path.join("data", "users.csv")
APPOINTMENTS_FILE = os.path.join("data", "appointments.csv")

# Dummy appointments loader
def load_appointments():
    try:
        return pd.read_csv(APPOINTMENTS_FILE)
    except:
        return pd.DataFrame(columns=["appointment_id", "staff_id", "patient_id", "date", "time", "type", "meeting_link"])

def load_logs():
    try:
        return pd.read_csv(LOGS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["patient_id", "date", "summary", "details"])
def save_log_to_file(patient_id, date, summary, details):
    df = load_logs()
    new_entry = pd.DataFrame([{
        "patient_id": patient_id,
        "date": date,
        "summary": summary,
        "details": details
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(LOGS_FILE, index=False)

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
    all_logs = load_logs()
    logs = all_logs[all_logs["patient_id"] == patient_id].to_dict("records")

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
import csv
from datetime import datetime

BILLING_FILE = "data/bills.csv"

def calculate_bill(appointment_type, insurance_level):
    base_prices = {
        "check up": 200,
        "emergency": 1000,
        "surgery": 5000,
        "follow up": 150
    }

    discounts = {
        "premium": 0.50,
        "standard": 0.30,
        "basic": 0.10,
        "none": 0.0
    }

    base_price = base_prices.get(appointment_type.lower(), 0)
    discount = discounts.get(insurance_level.lower(), 0)
    return round(base_price * (1 - discount), 2)

def end_appointment(appointment):
    st.subheader("🏁 End Appointment & Generate Bill")

    patient_id = appointment["patient_id"]
    patient_df = pd.read_csv(USERS_FILE)
    patient = patient_df[patient_df["user_id"] == patient_id].iloc[0]

    insurance_level = patient.get("insurance_level", "none") or "none"
    final_bill = calculate_bill(appointment["type"], insurance_level)

    st.markdown(f"**Appointment Type:** {appointment['type']}")
    st.markdown(f"**Patient Insurance Level:** {insurance_level.capitalize()}")
    st.markdown(f"💰 **Final Bill:** AED {final_bill}")

    if st.button("✔️ Confirm & Save Bill"):
        bill_entry = {
            "bill_id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "appointment_id": appointment["appointment_id"],
            "appointment_type": appointment["type"],
            "insurance_level": insurance_level,
            "amount": final_bill,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to CSV
        file_exists = os.path.exists(BILLING_FILE)
        with open(BILLING_FILE, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=bill_entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(bill_entry)

        st.success("✅ Bill saved successfully.")

        # ✅ Remove appointment
        appointments_df = load_appointments()
        appointments_df = appointments_df[appointments_df["appointment_id"] != appointment["appointment_id"]]
        appointments_df.to_csv(APPOINTMENTS_FILE, index=False)

        st.session_state.staff_page = "Schedule"
        st.rerun()


def log_details():
    # Get patient_id and log_index from session_state
    patient_id = st.session_state.get("selected_patient_id")
    log_index = st.session_state.get("selected_log_index")

    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("← Back"):
            st.session_state.staff_page = "patient_details"
            st.rerun()

    # Check for missing selections
    if patient_id is None or log_index is None:
        st.warning("Missing patient or log selection.")
        return

    all_logs = load_logs()
    logs = all_logs[all_logs["patient_id"] == patient_id].to_dict("records")

    # Check if log_index is out of bounds
    if log_index >= len(logs):
        st.warning("Log not found.")
        return

    log = logs[log_index]

    try:
        df = pd.read_csv(USERS_FILE)
        patient = df[df["user_id"] == patient_id].iloc[0]
    except Exception as e:
        st.error(f"Error loading patient info: {e}")
        return

    st.title(f"🗂️ Detailed Log for {patient['name']}")
    st.markdown(f"**Date:** {log['date']}")
    st.markdown(f"**Summary:** {log['summary']}")
    st.markdown(f"**Detailed Notes:**\n{log['details']}")
    st.divider()

    st.markdown("### 🧠 AI Diagnosis Suggestion")

    if st.button("💬 Get Medical Suggestion via GPT"):
        with st.spinner("Contacting AI..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are a helpful medical assistant to a doctor. Provide suggestions based on symptoms."},
                    {"role": "user", "content": f"Patient log summary: {log['summary']}\nDetails: {log['details']}"}
                ],
                temperature=0.5,
                max_tokens=200
            )
            suggestion = response.choices[0].message.content
            st.session_state.generated_chat_suggestion = suggestion

    if st.session_state.get("generated_chat_suggestion"):
        st.info(st.session_state["generated_chat_suggestion"])

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
            }
            save_log_to_file(patient_id, log_date, summary, details)
            st.success("Log saved successfully.")
            st.session_state.staff_page = "patient_details"
            st.rerun()
        else:
            st.warning("Please fill in all fields.")

def appointment_schedule():
    if st.button("← Back to Dashboard"):
        st.session_state.staff_page = "Dashboard"
        st.rerun()
    st.title("Appointment Schedule")



    user = st.session_state.get("user", {
        "user_id": 1,
        "role": "Staff",
        "schedule": "9AM–5PM",
        "position": "General Physician"
    })

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
                if st.button("🧾 End Appointment & Generate Bill", key=f"end_appt_{appt['appointment_id']}"):
                    st.session_state.selected_appointment = appt.to_dict()  # Fix this to use the current appointment
                    st.session_state.staff_page = "end_appointment"
                    st.rerun()

                if st.button(f"🛠 Modify Appointment {appt['appointment_id']}",
                             key=f"mod_appt_{appt['appointment_id']}"):
                    st.session_state.modify_appt_id = appt['appointment_id']
                    st.rerun()

                if st.session_state.get("modify_appt_id") == appt['appointment_id']:
                    with st.form(f"modify_form_{appt['appointment_id']}"):
                        new_date = st.date_input("Date", pd.to_datetime(appt['date']))
                        new_time = st.time_input("Time", pd.to_datetime(appt['time']).time())
                        new_type = st.selectbox(
                            "Appointment Type",
                            ["check up", "emergency", "surgery", "follow up"],
                            index=["check up", "emergency", "surgery", "follow up"].index(appt['type']) if appt[
                                                                                                               'type'] in [
                                                                                                               "check up",
                                                                                                               "emergency",
                                                                                                               "surgery",
                                                                                                               "follow up"] else 0
                        )
                        new_link = st.text_input("Meeting Link", appt['meeting_link'])
                        submitted = st.form_submit_button("💾 Save Changes")

                        if submitted:
                            appointments.loc[
                                appointments['appointment_id'] == appt['appointment_id'], ['date', 'time', 'type',
                                                                                           'meeting_link']] = [
                                str(new_date), str(new_time), new_type, new_link
                            ]
                            appointments.to_csv(APPOINTMENTS_FILE, index=False)
                            st.success("Appointment updated!")
                            del st.session_state.modify_appt_id
                            st.rerun()


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
        case "end_appointment":
            end_appointment(st.session_state.selected_appointment)
        case _:
            render_staff_home()

# Run the dashboard
staff_dashboard()
