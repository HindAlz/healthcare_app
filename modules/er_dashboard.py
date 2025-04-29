import streamlit as st
import pandas as pd
from datetime import datetime
import random


# Load emergency cases from CSV
@st.cache_data
def load_emergencies():
    try:
        df = pd.read_csv('data/appointments.csv')
        emergencies = df[df['type'].str.contains('Emergency', case=False)]

        if not emergencies.empty:
            # Add emergency-specific fields
            emergencies['severity'] = ['High', 'Critical', 'Medium'][:len(emergencies)]
            emergencies['status'] = ['New', 'In Progress'][:len(emergencies)]
            emergencies['location'] = ['123 Main St', '456 Oak Ave', '789 Pine Rd'][:len(emergencies)]
        return emergencies

    except FileNotFoundError:
        st.error("Emergency data file not found")
        return pd.DataFrame()


# ER Staff Dashboard
def er_dashboard():
    st.title("Emergency Cases Dashboard")

    # Load emergency data
    df_emergencies = load_emergencies()

    if df_emergencies.empty:
        st.warning("No emergency cases found")
        return

    # Create display IDs if they don't exist
    if 'appointment_id' not in df_emergencies.columns:
        df_emergencies['appointment_id'] = range(1, len(df_emergencies) + 1)

    # Search section
    st.subheader("Search Emergency Cases")
    search_query = st.text_input(
        "Search by Patient ID or Case ID",
        "",
        placeholder="Enter ID (e.g., 1 or 1001)"
    )

    # Apply search filter
    filtered_data = df_emergencies.copy()
    if search_query:
        filtered_data = filtered_data[
            filtered_data['patient_id'].astype(str).str.contains(search_query, case=False) |
            filtered_data['appointment_id'].astype(str).str.contains(search_query, case=False)
            ]

    # Emergency cases table
    st.subheader("Active Emergency Cases")
    st.dataframe(
        filtered_data[["appointment_id", "patient_id", "type", "severity", "date", "time", "status"]],
        column_config={
            "appointment_id": "Case ID",
            "patient_id": "Patient ID",
            "type": "Emergency Type",
            "severity": "Severity",
            "date": "Date",
            "time": "Time",
            "status": "Status"
        },
        hide_index=True,
        use_container_width=True
    )

    # Detailed view when a case is selected
    if search_query and not filtered_data.empty:
        case_data = filtered_data.iloc[0]

        st.divider()
        st.subheader(f"Emergency Details: Case #{case_data['appointment_id']}")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(f"""
            **Patient ID:** {case_data['patient_id']}  
            **Emergency Type:** {case_data['type']}  
            **Severity:** {case_data['severity']}  
            **Status:** {case_data['status']}  
            **Reported On:** {case_data['date']} at {case_data['time']}  
            **Location:** {case_data.get('location', 'Unknown')}
            """)

            # Simulated map
            st.markdown("### Emergency Location")
            st.image("https://cdn.prod.website-files.com/5c29380b1110ec92a203aa84/66e5ce469b48938aa34d8684_Google%20Maps%20-%20Compressed.jpg",
                     caption=f"Location: {case_data.get('location', 'Unknown')}")

        with col2:
            st.markdown("### Emergency Response")
            if st.button("Dispatch Ambulance", type="primary"):
                st.success("Ambulance dispatched to location")


# For testing without the full app
if __name__ == "__main__":
    er_dashboard()