from flask import Blueprint, request, jsonify
from models import db, Appointment, Prescription

bp = Blueprint('doctors', __name__, url_prefix='/doctors')

@bp.route('/<int:doctor_id>/appointments', methods=['GET'])
def get_appointments(doctor_id):
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    return jsonify([{
        'id': appt.id,
        'patient_id': appt.patient_id,
        'date': appt.date,
        'time': appt.time
    } for appt in appointments])

@bp.route('/<int:appointment_id>/prescribe', methods=['POST'])
def record_prescription(appointment_id):
    data = request.json
    prescription = Prescription(
        appointment_id=appointment_id,
        details=data['details']
    )
    db.session.add(prescription)
    db.session.commit()
    return jsonify({'message': 'Prescription recorded successfully'}), 201
@bp.route('/<int:doctor_id>/prescriptions', methods=['GET'])
def get_prescriptions(doctor_id):
    prescriptions = Prescription.query.join(Appointment).filter(Appointment.doctor_id == doctor_id).all()
    return jsonify([{
        'id': presc.id,
        'appointment_id': presc.appointment_id,
        'details': presc.details
    } for presc in prescriptions])

