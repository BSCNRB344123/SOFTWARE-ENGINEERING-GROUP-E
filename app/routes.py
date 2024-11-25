from flask import render_template, redirect, url_for, flash, request, abort
from app import app, db
from app.forms import (PatientRegistrationForm, AppointmentBookingForm, 
                       DoctorDashboardForm, DoctorRegistrationForm, PatientLoginForm, DoctorLoginForm, ReceptionistRegistrationForm, ReceptionistLoginForm)
from app.models import Patient, Doctor, Appointment, Prescription, User, Receptionist
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing
from flask_login import login_user, logout_user, login_required, current_user # Flask-Login
from sqlalchemy.exc import IntegrityError  # For handling IntegrityError
from functools import wraps

# Decorator to restrict access to doctors only
def doctor_required(f):  # New decorator
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.doctor:  # Check for doctor role/association with User
            flash('This page is only accessible to doctors.', 'danger')
            return redirect(url_for('doctor_login'))  # Redirect to doctor login
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')  # Render the index page

@app.route('/login', methods=['GET', 'POST'])  # Renamed to patient_login
def patient_login():    # Renamed to patient_login to be explicit
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PatientLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('patient_login'))
        patient = Patient.query.filter_by(user_id=user.id).first()
        if not patient:  # Check if logged-in user is associated with a Patient record
            flash('Not registered as a patient.', 'danger')
            return redirect(url_for('patient_login'))

        login_user(user)
        next_page = request.args.get('next')  # Handle "next" parameter for redirects
        return redirect(next_page) if next_page else redirect(url_for('book_appointment'))
    return render_template('patient_login.html', form=form)

@app.route('/doctor/login', methods=['GET', 'POST'])   # New route
def doctor_login():
    if current_user.is_authenticated:
        return redirect(url_for('doctor_dashboard', doctor_id=current_user.doctor.id)) #Redirect to dashboard if logged in
    form = DoctorLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('doctor_login'))

        doctor = Doctor.query.filter_by(user_id = user.id).first() # Check if a doctor is associated with this user
        if not doctor: # Check if no doctor exists
            flash('Not registered as a doctor.', 'danger')
            return redirect(url_for('doctor_login'))
        login_user(user)
        next_page = request.args.get('next')
        flash(f'Login Successful. Welcome {user.username}!', 'success')
        return redirect(next_page) if next_page else redirect(url_for('doctor_dashboard', doctor_id=doctor.id))
    return render_template('doctor_login.html', title='Doctor Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/patients/register', methods=['GET', 'POST'])
def register_patient():
    form = PatientRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        
        patient = Patient(
            name=form.name.data,
            dob=form.dob.data,
            address=form.address.data,
            user=user # Associate the user with the patient
        )
        db.session.add(patient)
        db.session.commit()
        flash('Patient registered successfully!', 'success')
        return redirect(url_for('patient_login')) 
    return render_template('register_patient.html', form=form)

@app.route('/doctor/register', methods=['GET', 'POST'])    # New route
def register_doctor():
    form = DoctorRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)

        doctor = Doctor(name=form.name.data, specialization=form.specialization.data, user=user) #Create doctor with association to user
        db.session.add(user)
        db.session.add(doctor)
        db.session.commit()
        flash('Doctor registered successfully!', 'success')
        return redirect(url_for('doctor_login'))  # Correct redirect
    return render_template('register_doctor.html', title='Register as a Doctor', form=form)


@app.route('/appointments/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    form = AppointmentBookingForm()
    doctors = Doctor.query.all()  # Query for all doctors
    if form.validate_on_submit():
        # Check Appointment Availability
        existing_appointment = Appointment.query.filter_by(
            doctor_id=form.doctor_id.data, date=form.date.data, time=form.time.data
        ).first()
        if existing_appointment:
            flash('Appointment slot already taken! Please choose a different time.', 'danger')
            return render_template('book_appointment.html', form=form) # Redisplay form with error

        try:
            patient = Patient.query.filter_by(user_id=current_user.id).first()

            if patient is None: # Check if no patient record exists
                flash('Patient not found!', 'danger')
                return redirect(url_for('register_patient')) #Or appropriate page
            
            appointment = Appointment(
                patient_id=form.patient_id.data,
                doctor_id=form.doctor_id.data,
                date=form.date.data,
                time=form.time.data,
            )
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment booked successfully!', 'success')  # Simple flash message
            return redirect(url_for('view_appointment', appointment_id=appointment.id)) # Redirect to view appointment page.
        except IntegrityError:  # Handle cases where patient or doctor IDs are invalid
            db.session.rollback()
            flash('Invalid patient or doctor ID.', 'danger')
        except Exception as e:  # Catch other potential errors
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
    if current_user.patients:  # Check for associated patient
        patient = current_user.patients[0]
        return render_template('book_appointment.html', form=form, doctors=doctors, patient=patient) # Pass doctors to template here
    else:
        flash("You haven't registered as a patient yet. Please register first.", 'danger')
        return redirect(url_for('register_patient'))
    
    return render_template('book_appointment.html', form=form)



@app.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id) # use get_or_404 to handle if appointment does not exist
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    if not current_user.doctor and patient.id != appointment.patient_id: # Check if logged-in user is the patient associated with the appointment
        abort(403) #If user is not authorized.

    try:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment cancelled successfully!', 'info')
    except Exception as e: # Handle any database or other exceptions during deletion
        db.session.rollback() # Rollback the session if an error occurs.
        flash(f"Error cancelling appointment: {e}", "danger") # Notify the user. Consider logging to server also.
        # Log the exception using app.logger or similar for debugging

    return redirect(url_for('index')) # Redirect after try block

@app.route('/appointments/<int:appointment_id>/view')
@login_required  # Protect the route
def view_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    # check if the current user is either the patient or doctor for the appointment.
    if not (current_user.doctor or (current_user.patients and patient.id == appointment.patient_id)): # Corrected logic
        abort(403)  # Access forbidden

    return render_template('appointment_details.html', appointment=appointment)



@app.route('/doctors/<int:doctor_id>/appointments', methods=['GET'])
@login_required
@doctor_required  # Apply the doctor_required decorator
def doctor_appointments(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if current_user.doctor.id != doctor.id:
        flash('Unauthorized access!', 'danger')  # Check if the logged-in user is the correct doctor
        return redirect(url_for('index'))
    appointments = doctor.appointments
    return render_template('doctor_appointments.html', doctor=doctor, appointments=appointments)


@app.route('/doctors/dashboard/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@doctor_required  # Apply the doctor_required decorator
def doctor_dashboard(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if current_user.doctor.id != doctor.id:
        flash('Unauthorized access!', 'danger')  # Check if the logged-in user is the correct doctor
        return redirect(url_for('index'))
    form = DoctorDashboardForm()

    if form.validate_on_submit():
        appointment = Appointment.query.get(form.appointment_id.data)
        if appointment:
            prescription = Prescription(
                appointment_id=appointment.id,
                details=form.prescription.data,
            )
            appointment.status = 'completed'
            db.session.add(prescription)
            db.session.commit()
            flash('Results recorded successfully!', 'success')
        else:
            flash('Appointment not found!', 'danger')
    
    appointments = doctor.appointments
    return render_template('doctor_dashboard.html', doctor=doctor, appointments=appointments, form=form)

@app.route('/receptionist/register', methods=['GET', 'POST'])
def receptionist_register():
    form = ReceptionistRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        receptionist = Receptionist(user=user) # create the receptionist record here, linked to user

        db.session.add(user)
        db.session.add(receptionist)  # Essential: Add the Receptionist object to the session
        db.session.commit()
        flash('Receptionist registered successfully!', 'success')
        return redirect(url_for('receptionist_login'))
    return render_template('receptionist_register.html', title='Receptionist Registration', form=form)

@app.route('/receptionist/login', methods=['GET', 'POST'])
def receptionist_login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ReceptionistLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('receptionist_login'))
        login_user(user)
        return redirect(url_for('receptionist_dashboard'))
    return render_template('receptionist_login.html', title='Receptionist Login', form=form)



@app.route('/receptionist/dashboard', methods=['GET', 'POST']) # new receptionist dashboard route
@login_required
def receptionist_dashboard():

    patients = Patient.query.all()  # Get all patients
    completed_appointments = Appointment.query.filter_by(status='completed').all()  # Get completed appointments


    return render_template('receptionist_dashboard.html', patients=patients, completed_appointments = completed_appointments)

@app.route('/patients/<string:patient_id>/deregister', methods=['POST'])
@login_required
def deregister_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Check if the user is a receptionist BY checking if Receptionist record exists for user
    receptionist = Receptionist.query.filter_by(user_id=current_user.id).first()

    if receptionist or patient.user_id == current_user.id:
        try:
            db.session.delete(patient)
            db.session.commit()
            flash('Patient deregistered successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deregistering patient: {e}', 'danger')
            app.logger.exception("Error deregistering patient") # Log the error for debugging.
    else:
        abort(403) # Correctly abort with 403 if unauthorized.

    return redirect(url_for('receptionist_dashboard')) # Or redirect based on user role

    # Determine the appropriate redirect based on user role:
    if current_user.receptionist:
        return redirect(url_for('receptionist_dashboard'))  # Redirect receptionist
    return redirect(url_for('index'))  # Redirect patient


@app.route('/appointments/<int:appointment_id>/remove', methods=['POST'])
@login_required
def remove_completed_appointment(appointment_id):

    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.status != 'completed':
        flash('Only completed appointments can be removed.', 'danger')
    else:
        try:
            db.session.delete(appointment)
            db.session.commit()
            flash('Appointment removed successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error removing appointment: {e}', 'danger')  # Provide a more specific error message

    return redirect(url_for('receptionist_dashboard')) #redirect to receptionist dashboard
