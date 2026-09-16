"""Domain objects used by the Streamlit prototype."""
class Patient:
    role = 'Patient'
    def __init__(self, patientID, name, personalInfo, medicalHistory=None):
        self.patientID = patientID
        self.name = name
        self.personalInfo = dict(personalInfo)
        self.medicalHistory = list(medicalHistory) if medicalHistory is not None else []

    def addHistory(self, day, month, year, details):
        self.medicalHistory.append({'date': f'{day:02d}-{month:02d}-{year:04d}', 'details': details})

class MedicalStaff:
    role = 'Staff'
    def __init__(self, staffID, name, personalInfo, schedule='', position=''):
        self.staffID = staffID
        self.name = name
        self.personalInfo = dict(personalInfo)
        self.schedule = schedule
        self.position = position

class ERStaff(MedicalStaff):
    role = 'ER'

class ManagementStaff(MedicalStaff):
    role = 'Admin'
    def __init__(self, staffID, name, personalInfo, schedule='', position='', resources=None):
        super().__init__(staffID, name, personalInfo, schedule, position)
        self.resources = list(resources) if resources is not None else []

class Appointment:
    def __init__(self, appointmentID, date, patientID, staffID, info, type):
        self.appointmentID = appointmentID
        self.date = date
        self.patientID = patientID
        self.staffID = staffID
        self.info = info
        self.type = type

class Bill:
    def __init__(self, billID, patientID, appointmentID, amount, paid=False):
        self.billID = billID
        self.patientID = patientID
        self.appointmentID = appointmentID
        self.amount = amount
        self.paid = paid
    def pay(self):
        self.paid = True

class Resource:
    def __init__(self, resourceID, name, expiryDate, stock):
        self.resourceID = resourceID
        self.name = name
        self.expiryDate = expiryDate
        self.stock = stock
    def restock(self, amount):
        if amount < 0:
            raise ValueError('Restock amount must be non-negative.')
        self.stock += amount
    def is_low(self):
        return self.stock < 10
