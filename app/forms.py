from wtforms import StringField, SubmitField, DateField, TimeField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Patient, Doctor, Appointment, Receptionist  # Import your models if needed for validation
from wtforms import IntegerField
from flask_wtf import FlaskForm

class PatientRegistrationForm(FlaskForm):
    # Fields for patient registration
    name = StringField('Name', validators=[DataRequired()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    address = StringField('Address')
    username = StringField('Username', validators=[DataRequired()])  # New
    password = PasswordField('Password', validators=[DataRequired()])  # New
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')]) # New for password confirmation
    submit = SubmitField('Register')

class AppointmentBookingForm(FlaskForm):
    # Fields for booking an appointment
    patient_id = StringField('Patient ID', validators=[DataRequired()])
    doctor_id = IntegerField('Doctor ID', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    submit = SubmitField('Book Appointment')

class DoctorRegistrationForm(FlaskForm):
    # Fields for doctor registration
    name = StringField('Name', validators=[DataRequired()])
    specialization = StringField('Specialization', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
class DoctorDashboardForm(FlaskForm):  # For recording results
    # Fields for recording appointment results
    appointment_id = IntegerField('Appointment ID', validators=[DataRequired()])
    outcome = TextAreaField('Outcome/Notes')
    prescription = TextAreaField('Prescription Details')
    submit = SubmitField('Record Results')

class PatientLoginForm(FlaskForm):
    # Fields for patient login
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class DoctorLoginForm(FlaskForm):
    # Fields for doctor login
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class ReceptionistRegistrationForm(FlaskForm):
    # Fields for receptionist registration
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ReceptionistLoginForm(FlaskForm):
    # Fields for receptionist login
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
