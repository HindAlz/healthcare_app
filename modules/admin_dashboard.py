import streamlit as st
import pandas as pd

# File paths
USER_FILE = "data/users.csv"
RESOURCE_FILE = "data/resources.csv"


# Load users (for staff management)
def load_users():
    try:
        return pd.read_csv(USER_FILE)
    except:
        return pd.DataFrame(columns=["user_id", "username", "password", "role", "name", "birthday", "email", "position",
                                     "specialization", "schedule"])


# Admin dashboard
def admin_dashboard():
    st.title("Admin Dashboard")

    # Admin-only functionality
    if st.session_state.user["role"] != "Admin":
        st.error("Access Denied: You are not authorized to view this page.")
        return

    st.sidebar.subheader("Admin Controls")
    choice = st.sidebar.selectbox("Manage", ["Staff Management", "Patient Management", "Resource Management"])

    if choice == "Staff Management":
        staff_management()

    if choice == "Patient Management":
        patient_management()

    if choice == "Resource Management":
        resource_management()


# Staff Management functionality
def staff_management():
    users = load_users()
    staff_members = users[users['role'] == 'Staff']

    st.subheader("Staff Management")
    st.write(staff_members[["user_id", "username", "name", "position", "specialization"]])

    staff_id = st.text_input("Search Staff ID to Edit or Delete")
    if staff_id:
        staff = staff_members[staff_members["user_id"] == int(staff_id)]
        if not staff.empty:
            st.write(staff)
            # Edit staff info
            position = st.text_input("Position", staff.iloc[0]["position"])
            specialization = st.text_input("Specialization", staff.iloc[0]["specialization"])
            schedule = st.text_input("Schedule", staff.iloc[0]["schedule"])
            if st.button("Save Changes"):
                users.loc[users["user_id"] == int(staff_id), ["position", "specialization", "schedule"]] = [position,
                                                                                                            specialization,
                                                                                                            schedule]
                users.to_csv(USER_FILE, index=False)
                st.success("Staff updated successfully!")
        else:
            st.error("Staff not found.")

import streamlit as st
import pandas as pd

# File paths
MEDICATION_FILE = "data/medications.csv"
DEVICE_FILE = "data/devices.csv"
CONSUMABLE_FILE = "data/consumables.csv"


# Load medications
def load_medications():
    try:
        return pd.read_csv(MEDICATION_FILE)
    except:
        return pd.DataFrame(columns=["medication_id", "name", "stock", "expiry_date"])


# Load devices
def load_devices():
    try:
        return pd.read_csv(DEVICE_FILE)
    except:
        return pd.DataFrame(columns=["device_id", "name", "amount_available", "next_maintenance_date"])


# Load consumables
def load_consumables():
    try:
        return pd.read_csv(CONSUMABLE_FILE)
    except:
        return pd.DataFrame(columns=["consumable_id", "name", "stock", "expiry_date"])


# Resource Management page
def resource_management():
    st.title("Resource Management")

    # Load user and check if role is admin
    user = st.session_state.user
    if user["role"] != "Admin":
        st.error("Access Denied: You are not authorized to view this page.")
        return

    st.sidebar.subheader("Resource Controls")
    choice = st.sidebar.selectbox("Choose a resource to manage", ["Medications", "Devices", "Consumables"])

    if choice == "Medications":
        manage_medications()

    elif choice == "Devices":
        manage_devices()

    elif choice == "Consumables":
        manage_consumables()

import streamlit as st
import pandas as pd

# Dummy patient data (replace with real data or DB connection)
patients_data = [
    {"patient_id": "P001", "name": "John Doe"},
    {"patient_id": "P002", "name": "Jane Smith"},
    {"patient_id": "P003", "name": "Ahmed Ali"}
]

appointments_data = {
    "P001": [
        {"appointment_id": "A101", "date": "2025-04-10", "type": "General Checkup", "status": "Paid"},
        {"appointment_id": "A102", "date": "2025-04-20", "type": "Diabetes Follow-up", "status": "In Progress"}
    ],
    "P002": [
        {"appointment_id": "A103", "date": "2025-03-15", "type": "Heart Screening", "status": "Paid"}
    ],
    "P003": [
        {"appointment_id": "A104", "date": "2025-04-01", "type": "ER Visit", "status": "Paid"},
        {"appointment_id": "A105", "date": "2025-04-12", "type": "Follow-up", "status": "In Progress"}
    ]
}

def patient_management():
    st.subheader("Patient Management")

    # Search bar
    search_id = st.text_input("Search by Patient ID")

    # Convert patient data to DataFrame
    df_patients = pd.DataFrame(patients_data)

    # Filtered display
    if search_id:
        df_patients = df_patients[df_patients["patient_id"].str.contains(search_id, case=False)]

    # Show patient list
    st.write("Patient List")
    st.dataframe(df_patients)

    # Select patient by ID
    selected_patient_id = st.selectbox("Select Patient ID", [p["patient_id"] for p in patients_data])
    st.write(f"Showing data for Patient ID: {selected_patient_id}")

    # Display appointment & billing history
    if selected_patient_id in appointments_data:
        st.markdown("### Past Appointments and Billing")
        df_appointments = pd.DataFrame(appointments_data[selected_patient_id])
        st.table(df_appointments)
    else:
        st.info("No appointment records found for this patient.")

    # Return button to go back to admin dashboard
    if st.button("Return to Admin Dashboard"):
        st.session_state["admin_page"] = "main"
        st.rerun()

# Manage Medications
def manage_medications():
    medications = load_medications()
    st.subheader("Manage Medications")
    st.write(medications[["medication_id", "name", "stock", "expiry_date"]])

    # Check for low stock and expiry
    low_stock = medications[medications["stock"] < 5]
    expiring = medications[pd.to_datetime(medications["expiry_date"]) < pd.to_datetime("today") + pd.Timedelta(days=30)]

    if not low_stock.empty:
        st.warning("Low stock medications:")
        st.write(low_stock)

    if not expiring.empty:
        st.warning("Medications nearing expiry:")
        st.write(expiring)

    # Option to restock
    medication_id = st.text_input("Enter Medication ID to Restock")
    if medication_id:
        restock_quantity = st.number_input("Quantity to Restock", min_value=1)
        if st.button("Restock"):
            medications.loc[medications["medication_id"] == int(medication_id), "stock"] += restock_quantity
            medications.to_csv(MEDICATION_FILE, index=False)
            st.success(f"Medication {medication_id} restocked successfully!")


# Manage Devices
def manage_devices():
    devices = load_devices()
    st.subheader("Manage Devices")
    st.write(devices[["device_id", "name", "amount_available", "next_maintenance_date"]])

    # Check for low stock and maintenance
    low_stock = devices[devices["amount_available"] < 3]
    maintenance_due = devices[
        pd.to_datetime(devices["next_maintenance_date"]) < pd.to_datetime("today") + pd.Timedelta(days=30)]

    if not low_stock.empty:
        st.warning("Devices with low stock:")
        st.write(low_stock)

    if not maintenance_due.empty:
        st.warning("Devices nearing maintenance:")
        st.write(maintenance_due)

    # Option to restock devices
    device_id = st.text_input("Enter Device ID to Restock")
    if device_id:
        restock_quantity = st.number_input("Quantity to Restock", min_value=1)
        if st.button("Restock Device"):
            devices.loc[devices["device_id"] == int(device_id), "amount_available"] += restock_quantity
            devices.to_csv(DEVICE_FILE, index=False)
            st.success(f"Device {device_id} restocked successfully!")


# Manage Consumables
def manage_consumables():
    consumables = load_consumables()
    st.subheader("Manage Consumables")
    st.write(consumables[["consumable_id", "name", "stock", "expiry_date"]])

    # Check for low stock and expiry
    low_stock = consumables[consumables["stock"] < 5]
    expiring = consumables[pd.to_datetime(consumables["expiry_date"]) < pd.to_datetime("today") + pd.Timedelta(days=30)]

    if not low_stock.empty:
        st.warning("Low stock consumables:")
        st.write(low_stock)

    if not expiring.empty:
        st.warning("Consumables nearing expiry:")
        st.write(expiring)

    # Option to restock consumables
    consumable_id = st.text_input("Enter Consumable ID to Restock")
    if consumable_id:
        restock_quantity = st.number_input("Quantity to Restock", min_value=1)
        if st.button("Restock Consumable"):
            consumables.loc[consumables["consumable_id"] == int(consumable_id), "stock"] += restock_quantity
            consumables.to_csv(CONSUMABLE_FILE, index=False)
            st.success(f"Consumable {consumable_id} restocked successfully!")
