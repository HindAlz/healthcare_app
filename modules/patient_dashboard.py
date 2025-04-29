import streamlit as st
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from models import Patient, MedicalStaff, ManagementStaff, Appointment, Bill, Resource
# File paths
APPOINTMENTS_FILE = "data/appointments.csv"
MEDICAL_HISTORY_FILE = "data/medical_history.csv"
BILLING_FILE = "data/bills.csv"

USERS_FILE = "data/users.csv"

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
def load_medical_histories(user_map):
    df = pd.read_csv("data/medical_history.csv")
    for _, row in df.iterrows():
        patient = user_map.get(row["patient_id"])
        if isinstance(patient, Patient):
            day, month, year = map(int, row["date"].split("-"))
            patient.addHistory(day, month, year, row["summary"])


# 1) Load bills into OOP objects
def load_bill_objects():
    df = pd.read_csv(BILLING_FILE)
    bills = []
    for _, row in df.iterrows():
        bill = Bill(
            billID = row["bill_id"],
            patientID = row["patient_id"],
            appointmentID = row["appointment_id"],
            amount = row["amount"],
            paid = (str(row.get("status","")).lower() == "paid")
        )
        bills.append(bill)
    return bills

# 2) Persist a list of Bill objects back to CSV by updating only the status column
# Persist all Bill objects back to the CSV
def save_bills_to_csv(bills):
    data = [{
        "bill_id": bill.billID,
        "patient_id": bill.patientID,
        "appointment_id": bill.appointmentID,
        "amount": bill.amount,
        "status": "Paid" if bill.paid else "Unpaid"
    } for bill in bills]

    df = pd.DataFrame(data)
    df.to_csv(BILLING_FILE, index=False)

# 3) The Streamlit view
def billing_information(user):
    # Ensure we have a Patient object
    user_map = load_user_objects()
    if isinstance(user, dict):
        user = user_map.get(user.get("user_id"))
        if not isinstance(user, Patient):
            st.error("Could not load your patient record.")
            return

    st.subheader("📄 Billing Information")

    bills = load_bill_objects()
    patient_bills = [b for b in bills if b.patientID == user.patientID]

    if not patient_bills:
        st.info("No billing information available.")
        return

    for bill in patient_bills:
        key = f"bill_{bill.billID}"
        with st.expander(f"Bill ID {bill.billID} (Appt {bill.appointmentID})"):
            st.write(f"💰 Amount: **${bill.amount:.2f}**")
            st.write(f"🛑 Status: **{'Paid' if bill.paid else 'Unpaid'}**")

            if bill.paid:
                st.write(f"✅ Already paid. [Download receipt](/receipts/{bill.billID}.pdf)")
            else:
                if st.button("Pay Now", key=key):
                    bill.pay()
                    save_bills_to_csv(bills)
                    st.success(f"Bill {bill.billID} marked as Paid.")
                    st.rerun()
# Sample Data (Replace with real data for more accuracy)
data = {
    'Family History': ['Yes', 'No', 'Yes', 'No', 'Yes'],
    'Physical Activity': ['Sedentary', 'Moderately Active', 'Sedentary', 'Very Active', 'Sedentary'],
    'Diet': ['Unhealthy', 'Healthy', 'Unhealthy', 'Healthy', 'Unhealthy'],
    'Weight Status': ['Obese', 'Normal', 'Overweight', 'Normal', 'Obese'],
    'Age Group': ['50+', '30–50', '30–50', 'Under 30', '50+'],
    'Thirst': ['Yes', 'No', 'Yes', 'No', 'Yes'],
    'Urination': ['Yes', 'No', 'Yes', 'No', 'Yes'],
    'Ethnicity': ['Hispanic', 'Caucasian', 'African-American', 'Asian', 'African-American'],
    'Diabetes Risk': ['High', 'Low', 'High', 'Low', 'High']
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Encode categorical values
df_encoded = df.copy()
df_encoded['Family History'] = df['Family History'].map({'Yes': 1, 'No': 0})
df_encoded['Physical Activity'] = df['Physical Activity'].map({'Sedentary': 0, 'Moderately Active': 1, 'Very Active': 2})
df_encoded['Diet'] = df['Diet'].map({'Healthy': 1, 'Unhealthy': 0})
df_encoded['Weight Status'] = df['Weight Status'].map({'Underweight': 0, 'Normal': 1, 'Overweight': 2, 'Obese': 3})
df_encoded['Age Group'] = df['Age Group'].map({'Under 30': 0, '30–50': 1, '50+': 2})
df_encoded['Thirst'] = df['Thirst'].map({'Yes': 1, 'No': 0})
df_encoded['Urination'] = df['Urination'].map({'Yes': 1, 'No': 0})
df_encoded['Ethnicity'] = df['Ethnicity'].map({'Caucasian': 0, 'Hispanic': 1, 'African-American': 2, 'Asian': 3, 'Other': 4})
df_encoded['Diabetes Risk'] = df['Diabetes Risk'].map({'High': 1, 'Low': 0})

# Train model
X = df_encoded.drop('Diabetes Risk', axis=1)
y = df_encoded['Diabetes Risk']
clf = DecisionTreeClassifier(random_state=42)
clf.fit(X, y)
# Streamlit app
def diabetes_risk_checker():
    st.title("🧪 Diabetes Risk Checker")
    st.info("Please answer the following questions to check your risk level:")

    family_history = st.radio("Do you have a family history of diabetes?", ("Yes", "No"))
    activity = st.radio("How would you describe your physical activity level?",
                        ("Sedentary", "Moderately Active", "Very Active"))
    diet = st.radio("How would you describe your dietary habits?", ("Healthy", "Unhealthy"))
    weight_status = st.radio("What is your weight status?", ("Underweight", "Normal", "Overweight", "Obese"))
    age_group = st.selectbox("Select your age group", ["Under 30", "30–50", "50+"])
    thirst = st.radio("Do you experience excessive thirst?", ("Yes", "No"))
    urination = st.radio("Do you experience frequent urination?", ("Yes", "No"))
    ethnicity = st.selectbox("Select your ethnicity", ["Caucasian", "Hispanic", "African-American", "Asian", "Other"])

    if st.button("Check My Risk"):
        # Encode inputs
        input_data = np.array([[
            1 if family_history == "Yes" else 0,
            {"Sedentary": 0, "Moderately Active": 1, "Very Active": 2}[activity],
            {"Healthy": 1, "Unhealthy": 0}[diet],
            {"Underweight": 0, "Normal": 1, "Overweight": 2, "Obese": 3}[weight_status],
            {"Under 30": 0, "30–50": 1, "50+": 2}[age_group],
            1 if thirst == "Yes" else 0,
            1 if urination == "Yes" else 0,
            {"Caucasian": 0, "Hispanic": 1, "African-American": 2, "Asian": 3, "Other": 4}[ethnicity]
        ]])

        # Make prediction
        prediction = clf.predict(input_data)[0]

        # Display result
        if prediction == 1:
            st.error("⚠️ You may be at high risk of diabetes. Please consult a doctor.")
        else:
            st.success("✅ You are at low risk based on the provided information.")
def patient_dashboard():
    st.title("Patient Dashboard")

    # Ensure the user is a Patient
    user = st.session_state.user
    if not isinstance(user, Patient):
        st.error("Access Denied: You are not authorized to view this page.")
        return

    # Sidebar profile using user attributes (directly from Patient object)
    st.sidebar.subheader(f"Profile: {user.name}")
    st.sidebar.text(f"Email: {user.personalInfo['email']}")
    st.sidebar.text(f"Birthday: {user.personalInfo['birthday']}")

    if "patient_view" not in st.session_state:
        st.session_state.patient_view = "dashboard"

    # Handle different views for the patient dashboard
    if st.session_state.patient_view == "dashboard":
        st.subheader("What would you like to do?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📅 Schedule Appointment"):
                st.session_state.patient_view = "schedule"
                st.rerun()

            if st.button("📄 Billing & Payment"):
                st.session_state.patient_view = "billing"
                st.rerun()

        with col2:
            if st.button("🩺 Medical History"):
                st.session_state.patient_view = "history"
                st.rerun()

            if st.button("📝 Update Info"):
                st.session_state.patient_view = "update"
                st.rerun()

        with col2:
            if st.button("🧪 Diabetes Risk Checker"):
                st.session_state.patient_view = "diabetes_check"
                st.rerun()

    elif st.session_state.patient_view == "schedule":
        if st.button("⬅️ Return to Dashboard"):
            st.session_state.patient_view = "dashboard"
            st.rerun()
        schedule_appointment(user)

    elif st.session_state.patient_view.startswith("modify_"):
        appointment_id = int(st.session_state.patient_view.replace("modify_", ""))
        modify_appointment(appointment_id)
        if st.button("⬅️ Return to Appointments"):
            st.session_state.patient_view = "schedule"
            st.rerun()

    elif st.session_state.patient_view == "billing":
        if st.button("⬅️ Return to Dashboard"):
            st.session_state.patient_view = "dashboard"
            st.rerun()
        billing_information(user)

    elif st.session_state.patient_view == "history":
        if st.button("⬅️ Return to Dashboard"):
            st.session_state.patient_view = "dashboard"
            st.rerun()
        view_medical_history(user)

    elif st.session_state.patient_view == "diabetes_check":
        if st.button("⬅️ Return to Dashboard"):
            st.session_state.patient_view = "dashboard"
            st.rerun()
        diabetes_risk_checker()

    elif st.session_state.patient_view == "update":
        if st.button("⬅️ Return to Dashboard"):
            st.session_state.patient_view = "dashboard"
            st.rerun()
        update_personal_info(user)

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
import datetime
import pandas as pd
import streamlit as st
from collections import defaultdict

# assumes these are already imported / defined:

import streamlit as st
import pandas as pd
from datetime import date, time
from datetime import date, time

def schedule_appointment(user: Patient):
    st.title("Your Appointments")

    user_map = load_user_objects()
    appointments = load_appointment_objects()

    # Filter this patient's appointments
    patient_appointments = [a for a in appointments if a.patientID == user.patientID]

    if not patient_appointments:
        st.info("You don't have any appointments yet.")
    else:
        st.subheader("Upcoming Appointments")
        for idx, appointment in enumerate(patient_appointments):
            staff = user_map.get(appointment.staffID)
            staff_name = staff.name if isinstance(staff, MedicalStaff) else "Unknown"

            date_str, time_str = appointment.date.split(" ")

            with st.expander(f"Appointment {appointment.appointmentID}"):
                st.write(f"📅 Date: **{date_str}**")
                st.write(f"⏰ Time: **{time_str}**")
                st.write(f"🧑 Doctor: **{staff_name}**")
                st.write(f"📄 Type: **{appointment.type}**")
                st.markdown(f"[🔗 Join Meeting]({appointment.info})", unsafe_allow_html=True)

                if st.button("🛠 Modify Appointment", key=f"mod_{appointment.appointmentID}"):
                    st.session_state.patient_view = f"modify_{appointment.appointmentID}"
                    st.rerun()

    st.markdown("---")

    # === Book New Appointment ===
    if "show_booking_form" not in st.session_state:
        st.session_state.show_booking_form = False

    if st.button("➕ Book Appointment"):
        st.session_state.show_booking_form = True

    if st.session_state.show_booking_form:
        with st.form("book_appointment_form"):
            st.subheader("Book a New Appointment")

            appt_date = st.date_input("Date", date.today())
            appt_time = st.time_input("Time", time(9, 0))
            appt_type = st.selectbox("Type", ["Consultation", "Checkup", "Emergency", "Follow-up"])

            staff_members = [u for u in user_map.values() if isinstance(u, MedicalStaff)]
            if not staff_members:
                st.warning("No staff available.")
                return

            selected_name = st.selectbox("Doctor", [s.name for s in staff_members])
            selected_staff = next(s for s in staff_members if s.name == selected_name)

            submitted = st.form_submit_button("➕ Confirm Booking")
            if submitted:
                new_id = max((a.appointmentID for a in appointments), default=0) + 1
                new_appt = Appointment(
                    appointmentID=new_id,
                    date=f"{appt_date} {appt_time}",
                    patientID=user.patientID,
                    staffID=selected_staff.staffID,
                    info=f"https://meet.example.com/{selected_staff.staffID}/{new_id}",
                    type=appt_type
                )
                appointments.append(new_appt)
                save_appointments_to_csv(appointments)
                st.success("Appointment booked successfully!")
                st.session_state.show_booking_form = False
                st.rerun()

# View Medical History
import pandas as pd
import pandas as pd
import streamlit as st

def view_medical_history(patient: Patient):
    st.subheader("📋 Your Medical History")

    # Lazy-load from CSV if not already populated
    if not patient.medicalHistory:
        df = pd.read_csv("data/logs.csv")
        # Filter rows for this patient
        for _, row in df[df["patient_id"] == patient.patientID].iterrows():
            # Assuming row["date"] is in "DD-MM-YYYY" or "YYYY-MM-DD" format
            parts = row["date"].split("-")
            # Try to parse day, month, year sensibly
            try:
                # If format is "YYYY-MM-DD"
                year, month, day = map(int, parts)
            except ValueError:
                # Fallback for "DD-MM-YYYY"
                day, month, year = map(int, parts)
            patient.addHistory(day, month, year, row["summary"])

    # Display
    if not patient.medicalHistory:
        st.info("No medical history available.")
    else:
        for entry in patient.medicalHistory:
            st.markdown(f"🗓️ **{entry['date']}** — {entry['details']}")

import os

# Function to save updated billing data
def save_billing(billing_data):
    billing_data.to_csv(BILLING_FILE, index=False)  # Save the updated DataFrame to the correct path
# Function to handle bill payment and status update
def pay_bill(appointment_id, amount):
    # Load all bills as Bill objects
    bills = load_bill_objects()

    # Find the bill for the given appointment ID
    bill = next((b for b in bills if b.appointmentID == appointment_id), None)
    if bill:
        # Mark as paid and update status
        bill.pay()

        # Save updated bills back to CSV
        save_bills_to_csv(bills)

        # Inform the user
        st.write(f"💳 Bill for Appointment {appointment_id} has been marked as paid.")
    else:
        st.error(f"No bill found for Appointment ID {appointment_id}.")

# Function to update the bill status to 'Paid' (same as paying the bill)
def update_bill_status(bill_id):
    # Load all bills as Bill objects
    bills = load_bill_objects()

    # Find the bill with the given bill_id
    bill = next((b for b in bills if b.billID == bill_id), None)
    if bill:
        # Mark as paid and update status
        bill.pay()

        # Save updated bills back to CSV
        save_bills_to_csv(bills)

        # Inform the user
        st.success(f"Bill {bill_id} has been updated to Paid.")
    else:
        st.error(f"No bill found with Bill ID {bill_id}.")

def save_users(users_df):
    users_df.to_csv(USERS_FILE, index=False)
import streamlit as st
from datetime import datetime

def update_personal_info(user: Patient):
    st.subheader("Update Personal Information")

    # Show current values from the Patient object
    name = st.text_input("Name", user.name)
    email = st.text_input("Email", user.personalInfo.get("email", ""))
    birthday = st.date_input(
        "Birthday",
        datetime.strptime(user.personalInfo.get("birthday", "2000-01-01"), "%Y-%m-%d")
    )

    if st.button("Save Changes"):
        # 1) Update the object in memory
        user.name = name
        user.personalInfo["email"] = email
        user.personalInfo["birthday"] = birthday.strftime("%Y-%m-%d")

        # 2) Persist updates to CSV
        df = pd.read_csv(USERS_FILE)
        # Find the row for this patient
        idx = df.index[df["user_id"] == user.patientID]
        if len(idx) == 0:
            st.error("User record not found in CSV.")
            return

        i = idx[0]
        df.at[i, "name"]     = name
        df.at[i, "email"]    = email
        df.at[i, "birthday"] = user.personalInfo["birthday"]
        df.to_csv(USERS_FILE, index=False)

        # 3) Refresh session state so dashboards see the updated object
        st.session_state.user = user

        st.success("Your information has been updated!")
# Modify Appointment
import streamlit as st
import pandas as pd
from datetime import datetime
def modify_appointment(appointment_id: int):
    appointments = load_appointment_objects()

    # Find the appointment by ID
    appointment = next((a for a in appointments if a.appointmentID == appointment_id), None)
    if appointment is None:
        st.error(f"No appointment found with ID {appointment_id}")
        return

    st.subheader(f"Modify Appointment {appointment_id}")

    # Split date/time string (assumes "YYYY-MM-DD HH:MM:SS")
    try:
        date_str, time_str = appointment.date.split(" ")
        current_date = pd.to_datetime(date_str).date()
        current_time = pd.to_datetime(time_str).time()
    except Exception:
        st.error("Error parsing date/time for this appointment.")
        return

    with st.form(key=f"modify_form_{appointment_id}"):
        new_date = st.date_input("Date", current_date)
        new_time = st.time_input("Time", current_time)

        # Use consistent casing in options
        type_options = ["Consultation", "Checkup", "Emergency", "Follow-up"]
        try:
            default_index = type_options.index(appointment.type)
        except ValueError:
            default_index = 0  # fallback if the type isn't in the list

        new_type = st.selectbox("Type", type_options, index=default_index)
        new_link = st.text_input("Meeting Link", appointment.info)

        submitted = st.form_submit_button("💾 Save Changes")
        if submitted:
            appointment.date = f"{new_date} {new_time}"
            appointment.type = new_type
            appointment.info = new_link

            save_appointments_to_csv(appointments)

            st.success("Appointment updated successfully!")
            st.session_state.modify_appt_id = None
            st.rerun()
