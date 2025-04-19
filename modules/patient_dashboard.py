import streamlit as st
import pandas as pd
import datetime

# File paths
APPOINTMENTS_FILE = "data/appointments.csv"
MEDICAL_HISTORY_FILE = "data/medical_history.csv"
BILLING_FILE = "data/bills.csv"

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
        return pd.DataFrame(columns=["bill_id","patient_id", "appointment_id","appointment_type", "bill_status","insurance_level", "amount","date","status"])


# Patient dashboard
def patient_dashboard():
    st.title("Patient Dashboard")

    # Load user and check if role is patient
    user = st.session_state.user
    if user["role"] != "Patient":
        st.error("Access Denied: You are not authorized to view this page.")
        return

    # Sidebar profile
    st.sidebar.subheader(f"Profile: {user['name']}")
    st.sidebar.text(f"Email: {user['email']}")
    st.sidebar.text(f"Birthday: {user['birthday']}")

    if "patient_view" not in st.session_state:
        st.session_state.patient_view = "dashboard"

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


    elif st.session_state.patient_view == "update":
        if st.button("⬅️ Return to Dashboard"):
            st.session_state.patient_view = "dashboard"
            st.rerun()
        update_personal_info(user)



# Schedule an Appointment
def schedule_appointment(user):
    st.title("Your Appointments")

    appointments = load_appointments()
    users = load_users()

    # Get patient's appointments
    patient_appointments = appointments[appointments["patient_id"] == user["user_id"]]

    if patient_appointments.empty:
        st.info("You don't have any appointments yet.")
    else:
        st.subheader("Upcoming Appointments")
        for idx, appointment in patient_appointments.iterrows():
            mod_key = f"mod_appt_{user['user_id']}_{appointment['appointment_id']}_{idx}"  # Add idx to make the key unique
            with st.expander(f"Appointment {appointment['appointment_id']}"):
                staff_member = users[users["user_id"] == appointment["staff_id"]]
                staff_name = staff_member["name"].values[0] if not staff_member.empty else "Unknown"

                st.write(f"📅 Date: **{appointment['date']}**")
                st.write(f"⏰ Time: **{appointment['time']}**")
                st.write(f"🧑 Doctor: **{staff_name}**")
                st.write(f"📄 Type: **{appointment['type']}**")
                st.markdown(f"[🔗 Join Meeting]({appointment['meeting_link']})", unsafe_allow_html=True)

                if st.button(f"🛠 Modify Appointment {appointment['appointment_id']}", key=mod_key):
                    st.session_state.modify_appt_id = appointment['appointment_id']
                    st.rerun()

                # Check if this is the appointment the user wants to modify
                if st.session_state.get("modify_appt_id") == appointment['appointment_id']:
                    with st.form(f"modify_form_{user['user_id']}_{appointment['appointment_id']}_{idx}"):  # Add idx to the form key
                        new_date = st.date_input("Date", pd.to_datetime(appointment['date']))
                        new_time = st.time_input("Time", pd.to_datetime(appointment['time']).time())
                        new_type = st.selectbox(
                            "Appointment Type",
                            ["check up", "emergency", "surgery", "follow up"],
                            index=["check up", "emergency", "surgery", "follow up"].index(appointment['type']) if
                            appointment['type'] in ["check up", "emergency", "surgery", "follow up"] else 0
                        )
                        new_link = st.text_input("Meeting Link", appointment['meeting_link'])
                        submitted = st.form_submit_button("💾 Save Changes")

                        if submitted:
                            appointments.loc[
                                appointments['appointment_id'] == appointment['appointment_id'], ['date', 'time', 'type',
                                                                                                  'meeting_link']] = [
                                str(new_date), str(new_time), new_type, new_link
                            ]
                            appointments.to_csv(APPOINTMENTS_FILE, index=False)
                            st.success("Appointment updated!")
                            del st.session_state.modify_appt_id
                            st.rerun()  # Reload the page to reflect changes

    st.markdown("---")

    # Button to show the booking form
    if 'show_booking_form' not in st.session_state:
        st.session_state.show_booking_form = False

    if st.button("➕ Book Appointment"):
        st.session_state.show_booking_form = True

    # Display the booking form conditionally
    if st.session_state.show_booking_form:
        with st.form("book_appointment_form"):
            st.subheader("Book a New Appointment")

            # Booking form
            appointment_date = st.date_input("Date", datetime.date.today())
            appointment_time = st.time_input("Time", datetime.time(9, 0))
            appointment_type = st.selectbox("Type", ["Consultation", "Checkup", "Emergency", "Follow-up"])

            staff_members = users[users["role"] == "Staff"]
            if staff_members.empty:
                st.warning("No staff available at the moment.")
                return

            selected_staff = st.selectbox("Doctor", staff_members["name"])
            staff_id = staff_members[staff_members["name"] == selected_staff]["user_id"].values[0]

            if st.form_submit_button("➕ Confirm Booking"):
                new_appointment = {
                    "appointment_id": len(appointments) + 1,
                    "date": appointment_date,
                    "time": appointment_time,
                    "patient_id": user["user_id"],
                    "staff_id": staff_id,
                    "type": appointment_type,
                    "meeting_link": f"https://meet.example.com/{staff_id}/{len(appointments) + 1}"
                }
                appointments = pd.concat([appointments, pd.DataFrame([new_appointment])], ignore_index=True)
                appointments.to_csv(APPOINTMENTS_FILE, index=False)
                st.success("Appointment booked successfully!")
                st.session_state.show_booking_form = False  # Hide the form after submission
                st.rerun()  # Reload the page to show the new appointment


# View Medical History
import pandas as pd

def view_medical_history(user):
    st.subheader("Your Medical History")

    # Load medical history from the CSV file
    medical_history = pd.read_csv('data/logs.csv')

    # Filter the medical history for the specific user based on their patient_id
    patient_history = medical_history[medical_history['patient_id'] == user['user_id']]

    if patient_history.empty:
        st.write("No medical history available.")
    else:
        st.write("Your Medical History:")
        # Only display the 'summary' column for the user
        st.write(patient_history[["summary"]])

import os

# Function to save updated billing data
def save_billing(billing_data):
    billing_data.to_csv(BILLING_FILE, index=False)  # Save the updated DataFrame to the correct path

def billing_information(user):
    st.subheader("Billing Information")

    billing_data = load_billing()

    # Filter the bills related to the logged-in user
    patient_bills = billing_data[billing_data['patient_id'] == user['user_id']]

    if patient_bills.empty:
        st.write("No billing information available.")
    else:
        for idx, bill in patient_bills.iterrows():
            mod_key = f"mod_bill_{user['user_id']}_{bill['appointment_id']}_{idx}"  # Add idx to make the key unique
            with st.expander(f"Bill for Appointment {bill['appointment_id']}"):
                st.write(f"📅 Appointment ID: **{bill['appointment_id']}**")
                st.write(f"🧑 Appointment Type: **{bill['appointment_type']}**")
                st.write(f"💰 Amount: **${bill['amount']}**")
                st.write(f"📅 Date: **{bill['date']}**")

                # Check if 'status' exists in the DataFrame
                if 'status' in bill:
                    st.write(f"🛑 Status: **{bill['status']}**")
                else:
                    st.write("🛑 Status: **Unknown**")

                if bill["status"] == "Paid":
                    st.write(f"Receipt: [Download Receipt](/path/to/receipt/{bill['appointment_id']})")
                elif st.button(f"Pay Bill for Appointment {bill['appointment_id']}", key=mod_key):
                    pay_bill(bill['appointment_id'], bill['amount'])

# Pay Bill
# Function to handle bill payment and status update
def pay_bill(appointment_id, amount):
    # Load the current billing data
    billing_data = load_billing()

    # Find the bill with the given appointment_id and update its status to "Paid"
    billing_data.loc[billing_data['appointment_id'] == appointment_id, 'status'] = 'Paid'

    # Save the updated billing data
    save_billing(billing_data)

    # Inform the user about the payment
    st.write(f"💳 Bill for Appointment {appointment_id} has been marked as paid.")

def update_bill_status(bill_id):
    billing_data = load_billing()

    # Find the bill and update the status
    bill_idx = billing_data[billing_data["bill_id"] == bill_id].index
    if not bill_idx.empty:
        billing_data.loc[bill_idx, "status"] = "Paid"
        save_billing(billing_data)
        st.success("Bill status updated to Paid.")


def save_users(users_df):
    users_df.to_csv(USERS_FILE, index=False)

def update_personal_info(user):
    st.subheader("Update Personal Information")

    # Create input fields for updating personal info
    name = st.text_input("Name", user.get("name", ""))
    email = st.text_input("Email", user.get("email", ""))
    birthday = st.date_input("Birthday", datetime.datetime.strptime(user.get("birthday", "2000-01-01"), "%Y-%m-%d"))

    if st.button("Save Changes"):
        # Update the session state
        st.session_state.user["name"] = name
        st.session_state.user["email"] = email
        st.session_state.user["birthday"] = str(birthday)

        # Load users from the CSV
        users = load_users()

        # Find the user by their user_id
        user_idx = users[users["user_id"] == user["user_id"]].index

        if not user_idx.empty:
            # Update the user's information
            users.loc[user_idx, "name"] = name
            users.loc[user_idx, "email"] = email
            users.loc[user_idx, "birthday"] = str(birthday)

            # Save the updated user data back to the CSV
            save_users(users)

            st.success("Your information has been updated.")
        else:
            st.error("User not found in the system.")

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
