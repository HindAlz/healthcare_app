import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime, date, time
from openai import OpenAI
from models import Patient, MedicalStaff, Appointment, Bill
APPOINTMENTS_FILE = "data/appointments.csv"
MEDICAL_HISTORY_FILE = "data/medical_history.csv"
BILLING_FILE = "data/bills.csv"

USERS_FILE = "data/users.csv"
import pandas as pd
from typing import Union, List
from models import Bill


def save_bills_to_csv(bills: Union[Bill, List[Bill]]):
    if isinstance(bills, Bill):
        bills = [bills]

    if not bills:
        return

    columns = [
        "bill_id",
        "patient_id",
        "appointment_id",
        "amount",
        "status",
    ]

    new_rows = pd.DataFrame([
        {
            "bill_id": str(bill.billID),
            "patient_id": bill.patientID,
            "appointment_id": bill.appointmentID,
            "amount": bill.amount,
            "status": "Paid" if bill.paid else "Unpaid",
        }
        for bill in bills
    ], columns=columns)

    try:
        existing = pd.read_csv(
            BILLING_FILE,
            dtype={"bill_id": str},
        )
    except (FileNotFoundError, pd.errors.EmptyDataError):
        existing = pd.DataFrame(columns=columns)

    # Replace matching bills while preserving all other bills.
    existing = existing[
        ~existing["bill_id"].isin(new_rows["bill_id"])
    ]

    updated = pd.concat(
        [existing, new_rows],
        ignore_index=True,
    )

    os.makedirs(os.path.dirname(BILLING_FILE), exist_ok=True)
    updated.to_csv(BILLING_FILE, index=False)


def save_appointments_to_csv(appointments: list):
    data = [{
        "appointment_id": a.appointmentID,
        "date": a.date.split(" ")[0],
        "time": a.date.split(" ")[1],
        "patient_id": a.patientID,
        "staff_id": a.staffID,
        "type": a.type,
        "meeting_link": a.info
    } for a in appointments]

    pd.DataFrame(data).to_csv("data/appointments.csv", index=False)

def load_user_objects():
    df = pd.read_csv("data/users.csv")
    user_objects = {}

    for _, row in df.iterrows():
        user_id = row["user_id"]
        name = row["name"]
        personal_info = {
            "email": row.get("email"),
            "birthday": row.get("birthday"),
            "username": row.get("username"),
            "specialization": row.get("specialization", ""),
        }

        if row["role"] == "Patient":
            user_objects[user_id] = Patient(user_id, name, personal_info)
        elif row["role"] == "Staff":
            user_objects[user_id] = MedicalStaff(
                user_id,
                name,
                personal_info,
                schedule=row.get("schedule", ""),
                position=row.get("position", "")
            )

    return user_objects

def load_appointment_objects():
    df = pd.read_csv("data/appointments.csv")
    appointments = []

    for _, row in df.iterrows():
        appt = Appointment(
            appointmentID=row["appointment_id"],
            date=f"{row['date']} {row['time']}",
            patientID=row["patient_id"],
            staffID=row["staff_id"],
            info=row["meeting_link"],
            type=row["type"]
        )
        appointments.append(appt)

    return appointments

# --- AI Setup ---
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None
APPOINTMENTS_FILE = "data/appointments.csv"
USERS_FILE = "data/users.csv"
LOGS_FILE = "data/logs.csv"

# --- Log ---
import pandas as pd

LOGS_FILE = "data/logs.csv"

def load_logs():
    try:
        df = pd.read_csv(LOGS_FILE)
        df["patient_id"] = df["patient_id"].astype(int)
        df["date"] = pd.to_datetime(df["date"])
        return df
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


def staff_dashboard():
    if "staff_page" not in st.session_state:
        st.session_state.staff_page = "Dashboard"
    match st.session_state.staff_page:
        case "Dashboard": render_staff_home()
        case "Patients": patient_management()
        case "Schedule": appointment_schedule()
        case "patient_details": patient_details()
        case "add_log": add_log()
        case "log_details": log_details()
        case "end_appointment": end_appointment(st.session_state.selected_appointment)

def render_staff_home():
    st.title("Staff Dashboard")
    col1, col2 = st.columns(2)
    if col1.button("🗓️ Appointment Schedule"):
        st.session_state.staff_page = "Schedule"
        st.rerun()
    if col2.button("👨‍⚕️ Patient Management"):
        st.session_state.staff_page = "Patients"
        st.rerun()

# --- Patient Management ---
def patient_management():
    st.title("Patient Management")
    if st.button("← Back to Dashboard"):
        st.session_state.staff_page = "Dashboard"
        st.rerun()

    users = load_user_objects()
    patients = [u for u in users.values() if isinstance(u, Patient)]
    if not patients:
        st.warning("No patients found.")
        return

    search = st.text_input("🔍 Search by name or ID:")
    if search:
        filtered = [p for p in patients if search.lower() in p.name.lower() or str(p.patientID) == search]
    else:
        filtered = patients

    df = pd.DataFrame([{
        "user_id": p.patientID,
        "name": p.name,
        "birthday": p.personalInfo.get("birthday"),
        "email": p.personalInfo.get("email")
    } for p in filtered])
    st.dataframe(df)

    ids = [p.patientID for p in filtered]
    selected_id = st.selectbox("Select a patient", ids)
    if selected_id and st.button("Show Info"):
        st.session_state.selected_patient_id = selected_id
        st.session_state.staff_page = "patient_details"
        st.rerun()

def patient_details():
    user_map = load_user_objects()
    patient = user_map.get(st.session_state.selected_patient_id)

    if not isinstance(patient, Patient):
        st.error("Patient not found.")
        return

    st.title(f"Patient Profile: {patient.name}")
    if st.button("← Back"):
        st.session_state.staff_page = "Patients"
        st.rerun()
    if st.button("➕ Add Log"):
        st.session_state.staff_page = "add_log"
        st.session_state.current_patient_id = patient.patientID
        st.rerun()

    st.image("https://via.placeholder.com/150", width=150)
    st.markdown(f"**Email:** {patient.personalInfo.get('email')}")
    st.markdown(f"**Birthday:** {patient.personalInfo.get('birthday')}")

    logs = [l for l in load_logs().to_dict("records") if l["patient_id"] == patient.patientID]
    if logs:
        st.subheader("📄 Visit Logs")
        st.dataframe(pd.DataFrame(logs)[["date", "summary"]])
        selected_log = st.selectbox("Select a log", range(len(logs)), format_func=lambda i: logs[i]["summary"])
        if st.button("➡️ Show Full Log Details"):
            st.session_state.selected_log_index = selected_log
            st.session_state.staff_page = "log_details"
            st.rerun()
    else:
        st.info("No logs for this patient.")

def add_log():
    st.title("Add New Log")
    if st.button("← Back to Patient"):
        st.session_state.staff_page = "patient_details"
        st.rerun()

    pid = st.session_state.get("current_patient_id")
    date_val = st.date_input("Date")
    summary = st.text_input("Summary")
    details = st.text_area("Detailed Notes")

    if st.button("Save Log"):
        if summary and details:
            save_log_to_file(pid, str(date_val), summary, details)
            st.success("Log saved.")
            st.session_state.staff_page = "patient_details"
            st.rerun()
        else:
            st.warning("All fields required.")


def log_details():
    pid = st.session_state.get("selected_patient_id")
    index = st.session_state.get("selected_log_index")
    logs = [l for l in load_logs().to_dict("records") if l["patient_id"] == pid]

    if index >= len(logs):
        st.warning("Log not found.")
        return
    log = logs[index]

    # Return button to go back to patient details
    if st.button("← Back to Patient Details"):
        st.session_state.staff_page = "patient_details"
        st.rerun()

    st.title("🗂️ Log Details")
    st.markdown(f"**Date:** {log['date']}")
    st.markdown(f"**Summary:** {log['summary']}")
    st.markdown(f"**Details:**\n{log['details']}")

    if st.button("💬 AI Suggestion"):
        if client is None:
            st.warning(
                "AI suggestions are disabled. "
                "Configure OPENAI_API_KEY locally to enable them."
            )
            return

        with st.spinner("Contacting GPT..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical assistant."},
                    {"role": "user", "content": f"Patient summary: {log['summary']}. Details: {log['details']}"}
                ]
            )
            suggestion = response.choices[0].message.content
            st.session_state.generated_chat_suggestion = suggestion

    if st.session_state.get("generated_chat_suggestion"):
        st.info(st.session_state["generated_chat_suggestion"])


import streamlit as st
from models import MedicalStaff, Appointment

def appointment_schedule():
    st.title("Appointment Schedule")

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.staff_page = "Dashboard"
        st.rerun()

    # 1. Ensure staff is a MedicalStaff object
    user = st.session_state.get("user")
    if not isinstance(user, MedicalStaff):
        st.error("Access Denied: Staff only.")
        return
    staff: MedicalStaff = user

    # 2. Load all appointments and filter
    appointments = load_appointment_objects()
    staff_appts = [a for a in appointments if a.staffID == staff.staffID]

    if not staff_appts:
        st.write("No appointments.")
        return

    # 3. Display each appointment
    for appt in staff_appts:
        with st.expander(f"Appointment {appt.appointmentID}"):
            st.write(f"📅 Date: **{appt.date}**")
            st.write(f"🧑 Patient ID: **{appt.patientID}**")
            st.write(f"📄 Type: **{appt.type}**")
            st.markdown(f"[🔗 Join Meeting]({appt.info})", unsafe_allow_html=True)

            # End & Bill button
            if st.button("🧾 End & Bill", key=f"end_{appt.appointmentID}"):
                st.session_state.selected_appointment = appt  # store the object
                st.session_state.staff_page = "end_appointment"
                st.rerun()

def calculate_bill(appointment_type: str, insurance_level: str) -> float:
    base_prices = {
        "checkup": 200,
        "check up": 200,
        "emergency": 1000,
        "surgery": 5000,
        "follow-up": 150,
        "follow up": 150,
        "consultation": 250,
    }

    discounts = {
        "premium": 0.50,
        "standard": 0.30,
        "basic": 0.10,
        "none": 0.0
    }

    base_type = appointment_type.strip().lower()
    base_price = base_prices.get(base_type, 0)

    level = insurance_level.strip().lower()
    discount = discounts.get(level, 0.0)

    final_price = base_price * (1 - discount)
    return round(final_price, 2)


def end_appointment(appointment_dict):
    # Extract the appointment details from the object and pass them as a dictionary
    appt = Appointment(**appointment_dict.__dict__)  # Use __dict__ to get the object's attributes

    st.subheader("🏁 End Appointment")
    users = load_user_objects()
    patient = users.get(appt.patientID)

    insurance = patient.personalInfo.get("insurance_level", "none") if patient else "none"
    amount = calculate_bill(appt.type, insurance)

    st.markdown(f"💰 **Amount:** AED {amount} (Insurance: {insurance.capitalize()})")

    if st.button("✔️ Confirm & Save Bill"):
        bill = Bill(str(uuid.uuid4()), appt.patientID, appt.appointmentID, amount, paid=False)
        save_bills_to_csv(bill)

        # Update the appointments list without this one
        appointments = [a for a in load_appointment_objects() if a.appointmentID != appt.appointmentID]
        save_appointments_to_csv(appointments)

        st.success("✅ Bill saved & appointment removed.")
        st.session_state.staff_page = "Schedule"
        st.rerun()
