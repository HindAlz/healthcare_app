import streamlit as st
import pandas as pd
import hashlib
import os
from datetime import datetime

from models import Patient, MedicalStaff, ManagementStaff  # adjust this import

USER_FILE = "data/users.csv"
os.makedirs("data", exist_ok=True)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users_df() -> pd.DataFrame:
    try:
        return pd.read_csv(USER_FILE)
    except FileNotFoundError:
        return pd.DataFrame(
            columns=[
                "user_id", "username", "password", "role", "name",
                "birthday", "email", "position", "specialization", "schedule"
            ]
        )

def save_users_df(df: pd.DataFrame):
    df.to_csv(USER_FILE, index=False)

def _make_user_object(row: pd.Series):
    """Helper: turn one user-row into a Patient or Staff object."""
    personal_info = {
        "email": row["email"],
        "birthday": row["birthday"],
        "username": row["username"],
        "specialization": row.get("specialization", ""),
    }
    role = row["role"]
    uid = row["user_id"]
    name = row["name"]

    if role == "Patient":
        return Patient(patientID=uid, name=name, personalInfo=personal_info)
    elif role == "Admin":
        # Admin gets ManagementStaff (with an empty resources list by default)
        return ManagementStaff(
            staffID=uid,
            name=name,
            personalInfo=personal_info,
            schedule=row.get("schedule", ""),
            position=row.get("position", ""),
            resources=[]
        )
    else:
        # Staff and ER both use MedicalStaff
        return MedicalStaff(
            staffID=uid,
            name=name,
            personalInfo=personal_info,
            schedule=row.get("schedule", ""),
            position=row.get("position", "")
        )

def login():
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log In"):
        df = load_users_df()
        user_row = df[df["username"] == username]
        if not user_row.empty:
            user_row = user_row.iloc[0]
            if user_row["password"] == hash_password(password):
                user_obj = _make_user_object(user_row)
                st.success("Login successful")
                return user_obj
        st.error("Invalid username or password.")
    return None


def sign_up():
    st.subheader("✍️ Sign Up")
    with st.form("signup_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        # Only allow "Patient" role to be selected
        role = st.selectbox("Role", ["Patient"])  # Removed Staff, Admin, ER options
        name = st.text_input("Full Name")
        birthday = st.date_input("Birthday")
        email = st.text_input("Email")


        submitted = st.form_submit_button("Create Account")
        if not submitted:
            return None

        # validate
        if password != confirm:
            st.error("Passwords do not match.")
            return None
        if not (username and password and name and email):
            st.error("Please fill all required fields.")
            return None

        # load & uniqueness
        df = load_users_df()
        if username in df["username"].values:
            st.error("Username already exists.")
            return None

        # append new row
        new_id = int(df["user_id"].max() or 0) + 1
        new_row = {
            "user_id": new_id,
            "username": username,
            "password": hash_password(password),
            "role": role,  # Always set to "Patient"
            "name": name,
            "birthday": birthday.strftime("%Y-%m-%d"),
            "email": email,

        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_users_df(df)

        # build and return the new object
        user_obj = _make_user_object(pd.Series(new_row))
        st.success("Account created! You can now log in.")
        return user_obj


# Example usage in your main Streamlit script:
def main():
    if "user" not in st.session_state:
        choice = st.radio("Choose action", ["Log In", "Sign Up"])
        if choice == "Log In":
            user = login()
        else:
            user = sign_up()

        if user:
            st.session_state.user = user
            st.experimental_rerun()

    # once logged in:
    if "user" in st.session_state:
        user = st.session_state.user
        st.write(f"👋 Hello, {user.name} ({type(user).__name__})")
        # … proceed to patient_dashboard(), staff_dashboard(), etc.

if __name__ == "__main__":
    main()
