"""Regression checks use synthetic records and never call the OpenAI API.

If Streamlit is absent, only its import is stubbed. These are business-logic
checks, not a browser/UI test suite.
"""
import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from datetime import date
import pandas as pd

if importlib.util.find_spec('streamlit') is None:
    sys.modules['streamlit'] = types.ModuleType('streamlit')

import storage
import auth
from models import Patient, ManagementStaff, MedicalStaff, ERStaff, Bill, Appointment
import services
from modules import patient_dashboard, staff_dashboard, admin_dashboard, er_dashboard
import app

class Regressions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original = storage.DATA_DIR
        storage.DATA_DIR = Path(self.temp.name)
        storage.ensure_data_files()
    def tearDown(self):
        storage.DATA_DIR = self.original
        self.temp.cleanup()
    def account(self, role='Patient', password=None, user_id=1):
        return {'user_id':user_id,'username':'demo','password':password or auth.hash_password('Synthetic-pass-123'),
                'role':role,'name':'Synthetic Person','birthday':'2000-01-01','email':'demo@example.com'}
    def test_patient_histories_and_resource_lists_are_isolated(self):
        a,b=Patient(1,'A',{}),Patient(2,'B',{})
        a.addHistory(1,2,2026,'Fictional note')
        self.assertEqual(b.medicalHistory,[])
        x,y=ManagementStaff(1,'X',{}),ManagementStaff(2,'Y',{})
        x.resources.append('demo');self.assertEqual(y.resources,[])
    def test_initialization_preserves_records(self):
        storage.write_table(pd.DataFrame([self.account()]),'users.csv')
        before=storage.table_path('users.csv').read_bytes()
        storage.ensure_data_files()
        self.assertEqual(before,storage.table_path('users.csv').read_bytes())
        self.assertEqual(patient_dashboard.load_bill_objects(),[])
        self.assertEqual(services.history_for(1),[])
    def test_first_signup_and_duplicate_username(self):
        u=auth.register_patient('demo','Synthetic-pass-123','Demo',date(2000,1,1),'demo@example.com')
        self.assertEqual(u.patientID,1)
        self.assertIsInstance(auth.authenticate('DEMO','Synthetic-pass-123'),Patient)
        with self.assertRaises(ValueError):
            auth.register_patient('DEMO','Synthetic-pass-123','Demo',date(2000,1,1),'demo@example.com')
    def test_password_salts_and_invalid_password(self):
        first=auth.hash_password('Synthetic-pass-123');second=auth.hash_password('Synthetic-pass-123')
        self.assertNotEqual(first,second)
        self.assertTrue(auth.verify_password('Synthetic-pass-123',first))
        self.assertFalse(auth.verify_password('wrong',first))
        self.assertFalse(auth.verify_password('x','pbkdf2_sha256$bad$bad$bad'))
    def test_legacy_hash_upgrade(self):
        old=hashlib.sha256(b'Synthetic-pass-123').hexdigest()
        storage.write_table(pd.DataFrame([self.account(password=old)]),'users.csv')
        self.assertIsNotNone(auth.authenticate('demo','Synthetic-pass-123'))
        self.assertTrue(storage.read_table('users.csv').iloc[0]['password'].startswith('pbkdf2_sha256$'))
    def test_roles_and_er_routing(self):
        for role,cls in [('Patient',Patient),('Staff',MedicalStaff),('Admin',ManagementStaff),('ER',ERStaff)]:
            user=auth._make_user_object(pd.Series(self.account(role)))
            self.assertIsInstance(user,cls)
            self.assertIsNotNone(app.dashboard_for(user))
        self.assertIs(app.dashboard_for(auth._make_user_object(pd.Series(self.account('ER')))),er_dashboard.er_dashboard)
        with self.assertRaises(ValueError):auth._make_user_object(pd.Series(self.account('Unknown')))
    def test_logout_clears_previous_patient_and_ai_state(self):
        class State(dict):
            def __setattr__(self,k,v):self[k]=v
        state=State(user='old',selected_patient_id=123,generated_chat_suggestion='old')
        with patch.object(app.st,'session_state',state,create=True):app.logout()
        self.assertEqual(state,{'user':None})
    def test_booking_labels_have_expected_prices(self):
        expected={'Consultation':250,'Checkup':200,'check up':200,'Emergency':1000,'Follow-up':150,'follow up':150,'Surgery':5000}
        for label,amount in expected.items():self.assertEqual(services.calculate_bill(label),amount)
        self.assertEqual(services.calculate_bill('Checkup','premium'),100)
        with self.assertRaises(ValueError):services.calculate_bill('Unknown')
    def test_new_bill_preserves_old_bills_and_payment_updates(self):
        old=Bill('old',1,1,200);new=Bill('new',2,2,150)
        staff_dashboard.save_bills_to_csv(old);staff_dashboard.save_bills_to_csv(new)
        self.assertEqual(len(storage.read_table('bills.csv')),2)
        old.pay();patient_dashboard.save_bills_to_csv([old])
        result=storage.read_table('bills.csv').set_index('bill_id')
        self.assertEqual(result.loc['old','status'],'Paid');self.assertEqual(result.loc['new','amount'],150)
    def test_finish_appointment_is_idempotent(self):
        row={'appointment_id':10,'date':'2026-10-01','time':'09:00:00','patient_id':1,'staff_id':2,'type':'Checkup','meeting_link':''}
        storage.write_table(pd.DataFrame([row]),'appointments.csv')
        appt=Appointment(10,'2026-10-01 09:00:00',1,2,'','Checkup')
        first=services.finish_appointment(appt);second=services.finish_appointment(appt)
        self.assertEqual(first.billID,second.billID)
        self.assertEqual(len(storage.read_table('bills.csv')),1)
        self.assertTrue(storage.read_table('appointments.csv').empty)
        self.assertEqual(list(storage.read_table('appointments.csv').columns),storage.SCHEMAS['appointments.csv'])
    def test_history_dates_and_patient_filtering(self):
        storage.write_table(pd.DataFrame([{'patient_id':1,'date':'2026-02-03','summary':'A','details':'Synthetic'},
                                         {'patient_id':2,'date':'04-02-2026','summary':'B','details':'Synthetic'}]),'logs.csv')
        self.assertEqual(services.history_for(1),[{'date':'03-02-2026','details':'A'}])
        self.assertEqual(services.history_for(2),[{'date':'04-02-2026','details':'B'}])
    def test_er_handles_many_emergencies_without_invented_severity(self):
        rows=[{'appointment_id':n,'date':'2026-10-01','time':'09:00:00','patient_id':1,'staff_id':2,'type':'Emergency','meeting_link':''} for n in range(10)]
        storage.write_table(pd.DataFrame(rows),'appointments.csv')
        df=er_dashboard.load_emergencies()
        self.assertEqual(len(df),10);self.assertEqual(set(df['severity']),{'Not recorded'})
    def test_empty_resource_tables_have_identifiers(self):
        for fn,id_column in [(admin_dashboard.load_medications,'med_id'),(admin_dashboard.load_devices,'device_id'),(admin_dashboard.load_consumables,'consumable_id')]:
            self.assertIn(id_column,fn().columns)
    def test_openai_is_optional_at_import(self):
        self.assertNotIn("client", vars(staff_dashboard))
        root = Path(__file__).resolve().parents[1]
        source_files = list(root.glob("*.py"))

        for folder in ("modules", "ai", "tests"):
            source_files.extend((root / folder).rglob("*.py"))

        for path in source_files:
            with self.subTest(file=str(path.relative_to(root))):
                self.assertNotIn(
                    "sk-" + "proj-",
                    path.read_text(encoding="utf-8"),
                )

if __name__=='__main__':unittest.main()
