from flask import Blueprint, request, jsonify
from models import db, Appointment, Doctor

bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@bp.route('/book', methods=['POST'])
def book_appointment():
    data = request.json
    appointment = Appointment(
        patient_id=data['patient_id'],
        doctor_id=data.get('doctor_id'),
        date=data['date'],
        time=data['time']
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment booked successfully'}), 201

@bp.route('/<int:id>/cancel', methods=['POST'])
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled successfully'}), 200
