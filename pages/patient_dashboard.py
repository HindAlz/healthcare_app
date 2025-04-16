import streamlit as st
import pandas as pd
import datetime

# File paths
APPOINTMENTS_FILE = "data/appointments.csv"
MEDICAL_HISTORY_FILE = "data/medical_history.csv"
BILLING_FILE = "data/billing.csv"

USERS_FILE = "data/users.csv"

def load_users():
    try:
        return pd.read_csv(USERS_FILE)
    except Exception:
        return pd.DataFrame(columns=["user_id", "username", "password", "role", "name", "birthday", "email", "position", "specialization", "schedule"])

# Load appointments
def load_appointments():
    try:
        return pd.read_csv(APPOINTMENTS_FILE)
    except Exception:
        return pd.DataFrame(
            columns=["appointment_id", "date", "time", "patient_id", "staff_id", "type", "meeting_link"])


# Load medical history
def load_medical_history():
    try:
        return pd.read_csv(MEDICAL_HISTORY_FILE)
    except Exception:
        return pd.DataFrame(columns=["patient_id", "appointment_id", "date", "summary", "test_results"])


# Load billing information
def load_billing():
    try:
        return pd.read_csv(BILLING_FILE)
    except Exception:
        return pd.DataFrame(columns=["patient_id", "appointment_id", "bill_status", "amount"])


# Patient dashboard
def patient_dashboard():
    st.title("Patient Dashboard")

    # Load user and check if role is patient
    user = st.session_state.user
    if user["role"] != "Patient":
        st.error("Access Denied: You are not authorized to view this page.")
        return

    # Display patient profile information
    st.sidebar.subheader(f"Profile: {user['name']}")
    st.sidebar.text(f"Email: {user['email']}")
    st.sidebar.text(f"Birthday: {user['birthday']}")

    # Display patient options
    st.subheader("What would you like to do?")
    choice = st.selectbox("Choose an option", ["Schedule an Appointment", "View Medical History", "Billing and Payment",
                                               "Update Personal Information"])

    if choice == "Schedule an Appointment":
        schedule_appointment(user)

    elif choice == "View Medical History":
        view_medical_history(user)

    elif choice == "Billing and Payment":
        billing_information(user)

    elif choice == "Update Personal Information":
        update_personal_info(user)

    # Return button to go back to the main dashboard
    if st.button("Log Out"):
        st.session_state.user = None  # Clear user session
        st.rerun()


# Schedule an Appointment
def schedule_appointment(user):
    st.subheader("Schedule an Appointment")

    # Load appointments and show available slots
    appointments = load_appointments()
    patient_appointments = appointments[appointments['patient_id'] == user['user_id']]

    if patient_appointments.empty:
        st.write("No upcoming appointments.")
    else:
        st.write("Your upcoming appointments:")
        for index, appointment in patient_appointments.iterrows():
            st.write(f"Appointment ID: {appointment['appointment_id']}")
            st.write(f"Date: {appointment['date']}, Time: {appointment['time']}")
            st.write(f"Doctor: {appointment['staff_id']}, Type: {appointment['type']}")
            st.write(f"Join link: [Join Meeting]({appointment['meeting_link']})")
            if st.button(f"Modify Appointment {appointment['appointment_id']}"):
                modify_appointment(appointment['appointment_id'])

    # Appointment form to book new appointment
    st.subheader("Book a New Appointment")
    appointment_date = st.date_input("Date", datetime.date.today())
    appointment_time = st.time_input("Time", datetime.time(9, 0))
    appointment_type = st.selectbox("Appointment Type", ["Consultation", "Checkup", "Emergency", "Follow-up"])
    users = load_users()
    staff_members = users[users["role"] == "Staff"]

    if staff_members.empty:
        st.warning("No staff available to book appointments.")
        return

    staff_options = staff_members["name"].tolist()
    selected_staff_name = st.selectbox("Doctor", staff_options)

    # Find the staff_id corresponding to the selected name
    staff_id = staff_members[staff_members["name"] == selected_staff_name]["user_id"].values[0]

    if st.button("Book Appointment"):
        new_appointment = {
            "appointment_id": len(appointments) + 1,
            "date": appointment_date,
            "time": appointment_time,
            "patient_id": user['user_id'],
            "staff_id": staff_id,
            "type": appointment_type,
            "meeting_link": f"https://meet.example.com/{staff_id}/{len(appointments) + 1}"
        }
        appointments = pd.concat([appointments, pd.DataFrame([new_appointment])], ignore_index=True)
        appointments.to_csv(APPOINTMENTS_FILE, index=False)
        st.success("Appointment booked successfully!")


# View Medical History
def view_medical_history(user):
    st.subheader("Your Medical History")

    medical_history = load_medical_history()
    patient_history = medical_history[medical_history['patient_id'] == user['user_id']]

    if patient_history.empty:
        st.write("No medical history available.")
    else:
        st.write("Your Medical History:")
        st.write(patient_history[["appointment_id", "date", "summary", "test_results"]])


# Billing and Payment
def billing_information(user):
    st.subheader("Billing Information")

    billing_data = load_billing()
    patient_bills = billing_data[billing_data['patient_id'] == user['user_id']]

    if patient_bills.empty:
        st.write("No billing information available.")
    else:
        for index, bill in patient_bills.iterrows():
            st.write(f"Appointment ID: {bill['appointment_id']}")
            st.write(f"Bill Status: {bill['bill_status']}")
            st.write(f"Amount: ${bill['amount']}")
            if bill["bill_status"] == "Paid":
                st.write(f"Receipt: [Download Receipt](/path/to/receipt/{bill['appointment_id']})")
            elif st.button(f"Pay Bill for Appointment {bill['appointment_id']}"):
                pay_bill(bill['appointment_id'], bill['amount'])


# Pay Bill
def pay_bill(appointment_id, amount):
    st.write(f"Proceeding to pay ${amount} for appointment ID {appointment_id}.")
    # Integrate billing API for secure transaction handling
    st.success("Payment successful!")

def update_personal_info(user):
    st.subheader("Update Personal Information")

    name = st.text_input("Name", user.get("name", ""))
    email = st.text_input("Email", user.get("email", ""))
    birthday = st.date_input("Birthday", datetime.datetime.strptime(user.get("birthday", "2000-01-01"), "%Y-%m-%d"))

    if st.button("Save Changes"):
        # Update the session state
        st.session_state.user["name"] = name
        st.session_state.user["email"] = email
        st.session_state.user["birthday"] = str(birthday)

        # Optionally, update the user in a database or user file
        # For now just show success
        st.success("Your information has been updated.")

# Modify Appointment
def modify_appointment(appointment_id):
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
