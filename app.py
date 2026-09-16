import streamlit as st
from auth import login, sign_up
from modules.patient_dashboard import patient_dashboard
from modules.staff_dashboard import staff_dashboard
from modules.admin_dashboard import admin_dashboard
from modules.er_dashboard import er_dashboard

from models import Patient, MedicalStaff, ManagementStaff  # adjust this import

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None

def logout():
    st.session_state.user = None
    st.rerun()

def main():
    st.set_page_config(page_title="Healthcare Management System", layout="wide")

    if st.session_state.user:
        # Access the role directly from the object
        role = getattr(
            st.session_state.user,
            "role",
            st.session_state.user.__class__.__name__
        )
        st.sidebar.success(f"Logged in as {st.session_state.user.name} ({role})")
        st.sidebar.button("Logout", on_click=logout)

        # Role-based dashboard navigation
        if isinstance(st.session_state.user, Patient):
            patient_dashboard()

        elif isinstance(st.session_state.user, ManagementStaff):
            admin_dashboard()
            
        elif role == "ER":
            er_dashboard()

        elif isinstance(st.session_state.user, MedicalStaff):
            staff_dashboard()

        else:
            st.error("Unknown user role.")

    else:
        st.title("Welcome to the Healthcare Management System")
        option = st.sidebar.radio("Select", ["Login", "Sign Up"])

        if option == "Login":
            user = login()
            if user:
                st.session_state.user = user
                st.rerun()  # Rerun to go to dashboard
        else:
            sign_up()

if __name__ == "__main__":
    main()
