import streamlit as st
import pandas as pd
import hashlib
import os

USER_FILE = "data/users.csv"
os.makedirs("data", exist_ok=True)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    try:
        return pd.read_csv(USER_FILE)
    except:
        return pd.DataFrame(columns=["user_id", "username", "password", "role", "name",
                                     "birthday", "email", "position", "specialization", "schedule"])


def save_users(df):
    df.to_csv(USER_FILE, index=False)


def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        users = load_users()
        user = users[users["username"] == username]
        if not user.empty and user.iloc[0]["password"] == hash_password(password):
            st.success("Login successful")
            return user.iloc[0].to_dict()
        else:
            st.error("Invalid username or password.")
    return None


def sign_up():
    st.subheader("Sign Up")
    with st.form("signup"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["Patient", "Staff", "Admin", "ER"])
        name = st.text_input("Full Name")
        birthday = st.date_input("Birthday")
        email = st.text_input("Email")
        position = st.text_input("Position (Staff/Admin only)")
        specialization = st.text_input("Specialization (Staff only)")
        schedule = st.text_input("Schedule (Staff only)")

        submitted = st.form_submit_button("Create Account")

        if submitted:
            if password != confirm:
                st.error("Passwords do not match")
                return

            if not username or not password or not name or not email:
                st.error("Please fill all required fields.")
                return

            users = load_users()
            if username in users["username"].values:
                st.error("Username already exists.")
                return

            new_user = {
                "user_id": len(users) + 1,
                "username": username,
                "password": hash_password(password),
                "role": role,
                "name": name,
                "birthday": birthday,
                "email": email,
                "position": position if role != "Patient" else "",
                "specialization": specialization if role == "Staff" else "",
                "schedule": schedule if role == "Staff" else ""
            }

            users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
            save_users(users)
            st.success("Account created successfully! Please login.")
