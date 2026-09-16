"""Local demo authentication with per-password salts and legacy hash migration."""
import hashlib
import hmac
import secrets
from datetime import date
import pandas as pd
import streamlit as st
from models import Patient, MedicalStaff, ManagementStaff, ERStaff
from storage import read_table, write_table, next_numeric_id

PBKDF2_ITERATIONS = 600_000

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS).hex()
    return f'pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}'

def verify_password(password, stored):
    if not isinstance(stored, str):
        return False
    try:
        if stored.startswith('pbkdf2_sha256$'):
            algorithm, rounds, salt, expected = stored.split('$')
            digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(rounds)).hex()
            return hmac.compare_digest(digest, expected)
        # Existing SHA-256 accounts can log in once and are then upgraded.
        if len(stored) == 64 and all(c in '0123456789abcdefABCDEF' for c in stored):
            return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), stored.lower())
    except (ValueError, TypeError, OverflowError):
        pass
    return False

def load_users_df():
    return read_table('users.csv')

def save_users_df(df):
    write_table(df, 'users.csv')

def _make_user_object(row):
    personal = {key: row.get(key, '') for key in ('email', 'birthday', 'username', 'specialization', 'insurance_level')}
    role = row['role']
    uid = int(row['user_id'])
    if role == 'Patient':
        return Patient(uid, row['name'], personal)
    classes = {'Admin': ManagementStaff, 'Staff': MedicalStaff, 'ER': ERStaff}
    if role not in classes:
        raise ValueError('Unknown account role.')
    return classes[role](uid, row['name'], personal, row.get('schedule', ''), row.get('position', ''))

def authenticate(username, password):
    df = load_users_df()
    matches = df.index[df['username'].str.casefold() == username.strip().casefold()]
    if len(matches) != 1:
        return None
    index = matches[0]
    stored = df.at[index, 'password']
    if not verify_password(password, stored):
        return None
    try:
        user = _make_user_object(df.loc[index])
    except ValueError:
        return None
    if not stored.startswith('pbkdf2_sha256$'):
        df.at[index, 'password'] = hash_password(password)
        save_users_df(df)
    return user

def register_patient(username, password, name, birthday, email):
    username, name, email = username.strip(), name.strip(), email.strip()
    if not all((username, password, name, email)):
        raise ValueError('Please fill all required fields.')
    if len(password) < 12:
        raise ValueError('Use a password with at least 12 characters.')
    if '@' not in email:
        raise ValueError('Enter a valid email address.')
    df = load_users_df()
    if username.casefold() in set(df['username'].str.casefold()):
        raise ValueError('Username already exists.')
    record = {'user_id': next_numeric_id(df, 'user_id'), 'username': username,
              'password': hash_password(password), 'role': 'Patient', 'name': name,
              'birthday': birthday.isoformat(), 'email': email,
              'position': '', 'specialization': '', 'schedule': ''}
    save_users_df(pd.concat([df, pd.DataFrame([record])], ignore_index=True))
    return _make_user_object(pd.Series(record))

def login():
    st.subheader('Login')
    with st.form('login_form'):
        username = st.text_input('Username', key='login_username')
        password = st.text_input('Password', type='password', key='login_password')
        submitted = st.form_submit_button('Log In')
    if submitted:
        user = authenticate(username, password)
        if user is not None:
            return user
        st.error('Invalid username or password.')
    return None

def sign_up():
    st.subheader('Create a patient account')
    with st.form('signup_form'):
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        confirm = st.text_input('Confirm Password', type='password')
        name = st.text_input('Full Name')
        birthday = st.date_input('Birthday', value=date(2000, 1, 1), min_value=date(1900, 1, 1), max_value=date.today())
        email = st.text_input('Email')
        submitted = st.form_submit_button('Create Account')
    if submitted:
        if password != confirm:
            st.error('Passwords do not match.')
            return
        try:
            register_patient(username, password, name, birthday, email)
        except ValueError as exc:
            st.error(str(exc))
            return
        st.success('Account created. Select Login to continue.')
