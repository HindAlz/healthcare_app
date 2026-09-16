import streamlit as st
from storage import ensure_data_files
from auth import login, sign_up
from modules.patient_dashboard import patient_dashboard
from modules.staff_dashboard import staff_dashboard
from modules.admin_dashboard import admin_dashboard
from modules.er_dashboard import er_dashboard

def dashboard_for(user):
    return {'Patient': patient_dashboard, 'Staff': staff_dashboard,
            'Admin': admin_dashboard, 'ER': er_dashboard}.get(getattr(user, 'role', None))

def logout():
    # Remove selected patients, logs and generated suggestions between accounts.
    st.session_state.clear()
    st.session_state.user = None

def main():
    st.set_page_config(page_title='Healthcare Management Prototype', layout='wide')
    ensure_data_files()
    st.session_state.setdefault('user', None)
    st.sidebar.caption('Educational prototype — use synthetic demo records.')
    if st.session_state.user is None:
        st.title('Healthcare Management Prototype')
        option = st.sidebar.radio('Select', ['Login', 'Sign Up'])
        if option == 'Login':
            user = login()
            if user is not None:
                st.session_state.clear()
                st.session_state.user = user
                st.rerun()
        else:
            sign_up()
        return
    user = st.session_state.user
    st.sidebar.success(f'Logged in as {user.name} ({user.role})')
    st.sidebar.button('Logout', on_click=logout)
    dashboard = dashboard_for(user)
    if dashboard is None:
        st.error('Unknown account role.')
        return
    dashboard()

if __name__ == '__main__':
    main()
