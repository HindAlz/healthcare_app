import streamlit as st
from auth import login, sign_up
from pages.patient_dashboard import patient_dashboard
from pages.staff_dashboard import staff_dashboard
from pages.admin_dashboard import admin_dashboard
from pages.er_dashboard import er_dashboard

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None

def logout():
    st.session_state.user = None
    st.rerun()

def main():
    st.set_page_config(page_title="Healthcare Management System", layout="wide")

    if st.session_state.user:
        role = st.session_state.user['role']
        st.sidebar.success(f"Logged in as {st.session_state.user['name']} ({role})")
        st.sidebar.button("Logout", on_click=logout)

        if role == "Patient":
            patient_dashboard()
        elif role == "Staff":
            staff_dashboard()
        elif role == "Admin":
            admin_dashboard()
        elif role == "ER":
            er_dashboard()
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
