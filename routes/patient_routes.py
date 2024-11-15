from flask import Blueprint, request, jsonify
from models import db, Patient
import uuid

bp = Blueprint('patients', __name__, url_prefix='/patients')

@bp.route('/register', methods=['POST'])
def register_patient():
    data = request.json
    patient_number = str(uuid.uuid4())[:10]  # Generate unique patient number
    patient = Patient(
        patient_number=patient_number,
        name=data['name'],
        dob=data['dob'],
        address=data['address']
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({'message': 'Patient registered successfully', 'patient_number': patient_number}), 201

@bp.route('/<int:id>', methods=['DELETE'])
def deregister_patient(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient de-registered successfully'}), 200
