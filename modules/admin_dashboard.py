import streamlit as st
import pandas as pd
from datetime import datetime
import os

# File paths
APPOINTMENTS_FILE = "data/appointments.csv"
MEDICAL_HISTORY_FILE = "data/medical_history.csv"
BILLING_FILE = "data/bills.csv"
USERS_FILE = "data/users.csv"
LOGS_FILE = os.path.join("data", "logs.csv")

# Load data functions
def load_users():
    try:
        return pd.read_csv(USERS_FILE)
    except:
        return pd.DataFrame(columns=["user_id", "username", "password", "role", "name", "birthday", "email", "position", "specialization", "schedule"])

def load_appointments():
    try:
        return pd.read_csv(APPOINTMENTS_FILE)
    except:
        return pd.DataFrame(columns=["appointment_id", "staff_id", "patient_id", "date", "time", "type", "meeting_link"])

def load_patient_data():
    try:
        users = load_users()
        return users[users['role'].str.lower() == 'patient'][["user_id", "name", "birthday", "email"]].rename(columns={"user_id": "patient_id"})
    except:
        return pd.DataFrame(columns=["patient_id", "name", "birthday", "email"])

def load_staff_data():
    try:
        users = load_users()
        staff = users[users['role'].str.lower() == 'staff']
        staff = staff.rename(columns={
            "user_id": "staff_id",
            "schedule": "working_hours",
            "position": "title"
        })
        return staff[["staff_id", "name", "specialization", "working_hours", "title", "email", "birthday"]]
    except:
        return pd.DataFrame(columns=["staff_id", "name", "specialization", "working_hours", "title", "email", "birthday"])

def load_medical_history():
    try:
        return pd.read_csv(MEDICAL_HISTORY_FILE)
    except:
        return pd.DataFrame(columns=["patient_id", "appointment_id", "date", "summary", "test_results"])

def load_billing():
    try:
        return pd.read_csv(BILLING_FILE)
    except:
        return pd.DataFrame(columns=["bill_id","patient_id", "appointment_id","appointment_type", "bill_status","insurance_level", "amount","date","status"])

def load_logs():
    try:
        return pd.read_csv(LOGS_FILE)
    except:
        return pd.DataFrame(columns=["patient_id", "date", "summary", "details"])

# Dummy resource data
def load_medications():
    return pd.DataFrame([{"med_id": "M001", "stock": 5, "expiry_date": "2025-05-01"}])

def load_devices():
    return pd.DataFrame([{"device_id": "D001", "available": 3, "next_maintenance": "2025-05-15"}])

def load_consumables():
    return pd.DataFrame([{"consumable_id": "C001", "stock": 6, "expiry_date": "2025-05-10"}])

# --- Admin Dashboard ---
def admin_dashboard():
    st.title("Admin Dashboard")

    # Default selected page
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = None

    # Navigation buttons
    if st.session_state.selected_page is None:
        col1, col2, col3 = st.columns(3)
        if col1.button("Staff Management"):
            st.session_state.selected_page = "staff_management"
            st.rerun()  # <== Force rerun after setting
        if col2.button("Patient Management"):
            st.session_state.selected_page = "patient_management"
            st.rerun()
        if col3.button("Resource Management"):
            st.session_state.selected_page = "resource_management"
            st.rerun()

    # Render selected section
    if st.session_state.selected_page == "staff_management":
        staff_management()
    elif st.session_state.selected_page == "patient_management":
        patient_management()
    elif st.session_state.selected_page == "resource_management":
        resource_management()



# Path to the CSV file


# Function to save data back to CSV
def save_users(df):
    df.to_csv(USERS_FILE, index=False)


import pandas as pd
import streamlit as st

# Path to the CSV file
USERS_FILE = "data/users.csv"


# Load data
def load_users():
    try:
        return pd.read_csv(USERS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["user_id", "username", "password", "role", "name", "birthday", "email", "position",
                                     "specialization", "schedule"])


# Function to save data back to CSV
def save_users(df):
    df.to_csv(USERS_FILE, index=False)


# --- Staff Management ---
def staff_management():
    # Initialize session state variables
    if "show_add_staff_form" not in st.session_state:
        st.session_state.show_add_staff_form = False
    if "show_staff_info" not in st.session_state:
        st.session_state.show_staff_info = False
    if "selected_staff_id" not in st.session_state:
        st.session_state.selected_staff_id = None

    # Return to Dashboard Button
    if st.button("🔙 Return to Dashboard"):
        st.session_state.selected_page = None
        st.stop()

    # Top Row Header + Add Button
    top1, top2 = st.columns([5, 1])
    with top1:
        st.header("Staff Management")
    with top2:
        if st.button("➕ Add New Staff"):
            st.session_state.show_add_staff_form = True
            st.session_state.show_staff_info = False
            st.session_state.selected_staff_id = None

    # Load and filter staff
    df = load_users()
    staff_df = df[df["role"] == "Staff"]

    # --- Staff Table + Selection ---
    search = st.text_input("Search Staff by ID or Name").lower()
    if search:
        staff_filtered = staff_df[
            staff_df["user_id"].str.contains(search) | staff_df["name"].str.lower().str.contains(search)
            ]
    else:
        staff_filtered = staff_df

    st.dataframe(staff_filtered[["user_id", "name", "specialization", "schedule"]], use_container_width=True)

    # Select staff to view/edit
    staff_ids = staff_filtered["user_id"].tolist()
    selected = st.selectbox("Select a Staff ID", staff_ids, key="select_staff_id")
    if st.button("View Info"):
        st.session_state.selected_staff_id = selected
        st.session_state.show_staff_info = True
        st.session_state.show_add_staff_form = False

    # --- View/Edit Staff Info ---
    if st.session_state.show_staff_info and st.session_state.selected_staff_id:
        staff = staff_df[staff_df["user_id"] == st.session_state.selected_staff_id].iloc[0]
        st.subheader(f"Staff Info: {staff['name']}")

        with st.form("edit_staff_form"):
            name = st.text_input("Name", value=staff["name"])
            specialization = st.text_input("Specialization", value=staff["specialization"])
            schedule = st.text_input("Schedule", value=staff["schedule"])
            email = st.text_input("Email", value=staff["email"])
            submit_edit = st.form_submit_button("💾 Save Changes")

            if submit_edit:
                df.loc[df["user_id"] == staff["user_id"], "name"] = name
                df.loc[df["user_id"] == staff["user_id"], "specialization"] = specialization
                df.loc[df["user_id"] == staff["user_id"], "schedule"] = schedule
                df.loc[df["user_id"] == staff["user_id"], "email"] = email
                save_users(df)
                st.success("✅ Staff info updated.")
                st.session_state.show_staff_info = False
                st.session_state.selected_staff_id = None
                st.rerun()

    # --- Add Staff Form ---
    if st.session_state.show_add_staff_form:
        st.subheader("Add New Staff")
        with st.form("new_staff_form"):
            new_id = st.text_input("User ID")
            username = st.text_input("Username")
            password = st.text_input("Password (hashed)")
            name = st.text_input("Name")
            birthday = st.date_input("Birthday")
            email = st.text_input("Email")
            position = st.text_input("Position")
            specialization = st.text_input("Specialization")
            schedule = st.text_input("Schedule")
            submit = st.form_submit_button("➕ Add Staff")

            if submit:
                new_entry = pd.DataFrame([{
                    "user_id": new_id,
                    "username": username,
                    "password": password,
                    "role": "Staff",
                    "name": name,
                    "birthday": birthday,
                    "email": email,
                    "position": position,
                    "specialization": specialization,
                    "schedule": schedule
                }])
                df = pd.concat([df, new_entry], ignore_index=True)
                save_users(df)
                st.success("✅ New staff added.")
                st.session_state.show_add_staff_form = False
                st.rerun()
def patient_management():
    if st.button("Return to Dashboard - Staff"):
        st.session_state.selected_page = None
        st.rerun()

    st.header("Patient Management")

    # Load data
    patients = load_patient_data()
    appointments = load_appointments()
    billing = load_billing()

    if patients.empty:
        st.warning("No patients found.")
        return

    # Search functionality
    search = st.text_input("Search Patient by ID or Name").lower()
    if search:
        patients_filtered = patients[
            patients["patient_id"].str.contains(search) | patients["name"].str.lower().str.contains(search)
        ]
    else:
        patients_filtered = patients

    # Display patient data
    st.dataframe(patients_filtered[["patient_id", "name", "birthday", "email"]], use_container_width=True)

    # Select a patient to view more details
    patient_ids = patients_filtered["patient_id"].tolist()
    selected = st.selectbox("Select a Patient ID", patient_ids, key="patient_select")

    if selected:
        patient_appointments = appointments[appointments["patient_id"] == selected]
        patient_billing = billing[billing["patient_id"] == selected]

        if patient_appointments.empty:
            st.info("No appointments found for this patient.")
        else:
            st.subheader("Appointment History")

            # Merge billing info into appointments
            merged = pd.merge(
                patient_appointments,
                patient_billing[["appointment_id", "status"]],
                on="appointment_id",
                how="left"
            ).rename(columns={"status": "Payment Status"})

            # Display each appointment with status and download option if paid
            for _, row in merged.iterrows():
                with st.expander(f"Appointment ID: {row['appointment_id']} — {row['date']}"):
                    st.write(f"**Type:** {row['type']}")
                    st.write(f"**Time:** {row['time']}")
                    status = row["Payment Status"] if pd.notna(row["Payment Status"]) else "Unpaid"
                    st.write(f"**Payment Status:** {status}")

                    if status.lower() == "paid":
                        # Create dummy receipt content
                        receipt_text = f"""
                        Receipt for Appointment {row['appointment_id']}
                        --------------------------------------
                        Patient ID: {selected}
                        Appointment Date: {row['date']}
                        Type: {row['type']}
                        Time: {row['time']}
                        Status: PAID
                        """
                        st.download_button(
                            label="Download Receipt",
                            data=receipt_text,
                            file_name=f"receipt_{row['appointment_id']}.txt",
                            mime="text/plain"
                        )
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# Path to the data folder
DATA_FOLDER = "data"

# Create the 'data' folder if it doesn't exist
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Function to load data from CSV files
def load_medications():
    return pd.read_csv(os.path.join(DATA_FOLDER, "medications.csv"))

def load_devices():
    return pd.read_csv(os.path.join(DATA_FOLDER, "devices.csv"))

def load_consumables():
    return pd.read_csv(os.path.join(DATA_FOLDER, "consumables.csv"))

# --- Resource Management ---
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# Path to the data folder
DATA_FOLDER = "data"

# Create the 'data' folder if it doesn't exist
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Function to load data from CSV files
def load_medications():
    return pd.read_csv(os.path.join(DATA_FOLDER, "medications.csv"))

def load_devices():
    return pd.read_csv(os.path.join(DATA_FOLDER, "devices.csv"))

def load_consumables():
    return pd.read_csv(os.path.join(DATA_FOLDER, "consumables.csv"))
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# Path to the data folder
DATA_FOLDER = "data"

# Create the 'data' folder if it doesn't exist
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Function to load data from CSV files
def load_medications():
    return pd.read_csv(os.path.join(DATA_FOLDER, "medications.csv"))

def load_devices():
    return pd.read_csv(os.path.join(DATA_FOLDER, "devices.csv"))

def load_consumables():
    return pd.read_csv(os.path.join(DATA_FOLDER, "consumables.csv"))
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# Path to the data folder
DATA_FOLDER = "data"

# Create the 'data' folder if it doesn't exist
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Function to load data from CSV files
def load_medications():
    return pd.read_csv(os.path.join(DATA_FOLDER, "medications.csv"))

def load_devices():
    return pd.read_csv(os.path.join(DATA_FOLDER, "devices.csv"))

def load_consumables():
    return pd.read_csv(os.path.join(DATA_FOLDER, "consumables.csv"))
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# Path to the data folder
DATA_FOLDER = "data"

# Create the 'data' folder if it doesn't exist
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Function to load data from CSV files
def load_medications():
    return pd.read_csv(os.path.join(DATA_FOLDER, "medications.csv"))

def load_devices():
    return pd.read_csv(os.path.join(DATA_FOLDER, "devices.csv"))

def load_consumables():
    return pd.read_csv(os.path.join(DATA_FOLDER, "consumables.csv"))
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# Path to the data folder
DATA_FOLDER = "data"

# Create the 'data' folder if it doesn't exist
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
import os
import pandas as pd
import streamlit as st
from datetime import datetime

DATA_FOLDER = "data"

def load_medications():
    path = os.path.join(DATA_FOLDER, "medications.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame(columns=["med_id", "name", "stock", "expiry_date", "low_stock"])

def load_devices():
    path = os.path.join(DATA_FOLDER, "devices.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame(columns=["device_id", "name", "available", "next_maintenance", "low_available"])

def load_consumables():
    path = os.path.join(DATA_FOLDER, "consumables.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame(columns=["consumable_id", "name", "stock", "expiry_date", "low_stock"])

def show_add_new_form(resource_type, df, file_path, id_prefix, fields):
    col1, col2 = st.columns([3, 1])
    form_key = f"{resource_type.lower()}_form_visible"

    with col2:
        if st.button(f"➕ Add New {resource_type}", key=f"add_{resource_type}_btn"):
            st.session_state[form_key] = True

    if st.session_state.get(form_key, False):
        with st.form(key=f"add_{resource_type}_form"):
            st.subheader(f"Add New {resource_type}")
            user_inputs = {}
            for label, input_type in fields:
                if input_type == "text":
                    user_inputs[label] = st.text_input(label)
                elif input_type == "number":
                    user_inputs[label] = st.number_input(label, min_value=1)
                elif input_type == "date":
                    user_inputs[label] = st.date_input(label)

            submit = st.form_submit_button("Add")
            if submit:
                if not df.empty:
                    last_id = df[df.columns[0]].str.extract(r"(\d+)$").dropna().astype(int).max()[0]
                    new_id = f"{id_prefix}{last_id + 1:03}"
                else:
                    new_id = f"{id_prefix}001"

                data = {df.columns[0]: new_id}
                i = 1
                for label, _ in fields:
                    value = user_inputs[label]
                    if isinstance(value, datetime):
                        value = value.strftime("%Y-%m-%d")
                    data[df.columns[i]] = value
                    i += 1

                new_df = pd.DataFrame([data])
                df = pd.concat([df, new_df], ignore_index=True)
                df.to_csv(file_path, index=False)
                st.success(f"{resource_type} added with ID {new_id}")
                st.session_state[form_key] = False
                st.rerun()
# --- Resource Management ---
def resource_management():
    if st.button("Return to Dashboard - Staff"):
        st.session_state.selected_page = None
        st.rerun()

    st.header("Resource Management")
    option = st.selectbox("Select Resource", ["Medications", "Devices", "Consumables"], key="resource_select")
    today = datetime.today().date()

    if option == "Medications":
        meds = load_medications()
        show_add_new_form(
            "Medication",
            meds,
            "data/medications.csv",
            "MED",
            fields=[
                ("name", "text"),
                ("stock", "number"),
                ("expiry_date", "date"),
                ("low_stock", "number")
            ]
        )
        st.dataframe(meds)

        # Warnings
        for _, row in meds.iterrows():
            if row["stock"] < row["low_stock"]:
                st.warning(f"Low stock for {row['med_id']}")
            expiry = datetime.strptime(row["expiry_date"], "%Y-%m-%d").date()
            if (expiry - today).days < 30:
                st.error(f"Medication {row['med_id']} nearing expiry on {row['expiry_date']}")

        # Individual restock
        selected = st.selectbox("Select medication to restock", meds["med_id"].tolist(), key="restock_med_select")
        if st.button("Restock Selected Medication", key="restock_med_btn"):
            meds.loc[meds["med_id"] == selected, "stock"] = meds.loc[meds["med_id"] == selected, "low_stock"]
            meds.to_csv("data/medications.csv", index=False)
            st.success(f"{selected} restocked to threshold.")
            st.rerun()

    elif option == "Devices":
        devices = load_devices()
        show_add_new_form(
            "Device",
            devices,
            "data/devices.csv",
            "DEV",
            fields=[
                ("name", "text"),
                ("available", "number"),
                ("next_maintenance", "date"),
                ("low_available", "number")
            ]
        )
        st.dataframe(devices)

        for _, row in devices.iterrows():
            if row["available"] < row["low_available"]:
                st.warning(f"Low availability for {row['device_id']}")
            next_maint = datetime.strptime(row["next_maintenance"], "%Y-%m-%d").date()
            if (next_maint - today).days < 30:
                st.error(f"Device {row['device_id']} needs maintenance soon ({row['next_maintenance']})")

        selected = st.selectbox("Select device to restock", devices["device_id"].tolist(), key="restock_device_select")
        if st.button("Restock Selected Device", key="restock_device_btn"):
            devices.loc[devices["device_id"] == selected, "available"] = devices.loc[devices["device_id"] == selected, "low_available"]
            devices.to_csv("data/devices.csv", index=False)
            st.success(f"{selected} restocked to threshold.")
            st.rerun()

    elif option == "Consumables":
        cons = load_consumables()
        show_add_new_form(
            "Consumable",
            cons,
            "data/consumables.csv",
            "CON",
            fields=[
                ("name", "text"),
                ("stock", "number"),
                ("expiry_date", "date"),
                ("low_stock", "number")
            ]
        )
        st.dataframe(cons)

        for _, row in cons.iterrows():
            if row["stock"] < row["low_stock"]:
                st.warning(f"Low stock for {row['consumable_id']}")
            expiry = datetime.strptime(row["expiry_date"], "%Y-%m-%d").date()
            if (expiry - today).days < 30:
                st.error(f"Consumable {row['consumable_id']} expiring soon ({row['expiry_date']})")

        selected = st.selectbox("Select consumable to restock", cons["consumable_id"].tolist(), key="restock_cons_select")
        if st.button("Restock Selected Consumable", key="restock_cons_btn"):
            cons.loc[cons["consumable_id"] == selected, "stock"] = cons.loc[cons["consumable_id"] == selected, "low_stock"]
            cons.to_csv("data/consumables.csv", index=False)
            st.success(f"{selected} restocked to threshold.")
            st.rerun()

# --- Run Dashboard ---
if __name__ == "__main__":
    admin_dashboard()
