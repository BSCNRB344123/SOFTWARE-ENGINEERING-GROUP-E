from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID  # Import even if using SQLite initially
import shortuuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):  # for debugging in console
        return f'<User {self.id} {self.username}>'
    
# Patient model
class Patient(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # String(36) for UUID storage
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)  # Date of Birth
    address = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), name='fk_patient_user') #add name = argument
    user = db.relationship("User", backref=db.backref("patients", lazy=True), foreign_keys=[user_id]) # foreign_key
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Patient {self.id} {self.name}>'

# Doctor model
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_doctor_user'))  # Add user_id and relationship
    user = db.relationship("User", backref=db.backref("doctor", uselist=False, lazy=True), foreign_keys=[user_id])  # One-to-one relationship
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

    def __repr__(self):  # For debugging
        return f'<Doctor {self.name} ({self.specialization})>'

# Appointment model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(36), db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # e.g., scheduled, cancelled, completed
    prescription = db.relationship('Prescription', backref='appointment', lazy=True, cascade="all, delete-orphan")  #One-to-many for Appointment-Prescription  

    def __repr__(self):
        return f'<Appointment {self.id}>'
    
# Prescription model
class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    details = db.Column(db.Text)

    def __repr__(self):
        return f'<Prescription {self.details}>'

# Receptionist model
class Receptionist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_receptionist_user'))
    user = db.relationship('User', backref=db.backref('receptionist', uselist=False, lazy=True), foreign_keys=[user_id])



