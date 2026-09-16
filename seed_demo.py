"""Create a fresh set of fictional accounts in data/demo; never overwrite records."""
import os
os.environ['HEALTHCARE_DATA_DIR'] = 'data/demo'
import getpass
from datetime import date, timedelta
import pandas as pd
from storage import read_table, write_table, SCHEMAS
from auth import hash_password

def seed(password):
    if len(password) < 12:
        raise ValueError('Use a demo password with at least 12 characters.')
    if any(not read_table(name).empty for name in SCHEMAS):
        raise ValueError('data/demo already contains records. No existing data was overwritten.')
    accounts=[]
    for uid, role in enumerate(['Patient','Staff','Admin','ER'],1):
        accounts.append({'user_id': uid, 'username': f'demo_{role.lower()}',
                         'password': hash_password(password), 'role':role,
                         'name': f'Demo {role}', 'birthday':'2000-01-01',
                         'email':f'{role.lower()}@example.com',
                         'position':role, 'specialization':'General Practice' if role=='Staff' else '',
                         'schedule':'Weekdays' if role=='Staff' else ''})
    write_table(pd.DataFrame(accounts),'users.csv')
    tomorrow=(date.today()+timedelta(days=1)).isoformat()
    write_table(pd.DataFrame([
        {'appointment_id':1,'date':tomorrow,'time':'09:00:00','patient_id':1,'staff_id':2,'type':'Checkup','meeting_link':''},
        {'appointment_id':2,'date':tomorrow,'time':'10:00:00','patient_id':1,'staff_id':2,'type':'Emergency','meeting_link':''}
    ]),'appointments.csv')
    later=(date.today()+timedelta(days=180)).isoformat()
    write_table(pd.DataFrame([{'med_id':'MED001','name':'Demo medication','stock':20,'expiry':later,'low_stock':10}]),'medications.csv')
    write_table(pd.DataFrame([{'device_id':'DEV001','name':'Demo device','available':3,'next_maintenance':later,'low_available':2}]),'devices.csv')
    write_table(pd.DataFrame([{'consumable_id':'CON001','name':'Demo consumable','stock':50,'expiry':later,'low_stock':20}]),'consumables.csv')

if __name__=='__main__':
    try:
        password=getpass.getpass('Choose a local demo password (12+ characters): ')
        if password!=getpass.getpass('Confirm password: '):
            raise ValueError('Passwords do not match.')
        seed(password)
    except ValueError as exc:
        raise SystemExit(str(exc))
    print('Created fictional accounts: demo_patient, demo_staff, demo_admin, demo_er.')
    print('Use your chosen password. Start the demo with: python run_demo.py')
