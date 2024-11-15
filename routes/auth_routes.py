from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

users = {}  # Example in-memory user storage for simplicity

@bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if data['username'] in users:
        return jsonify({'message': 'User already exists'}), 400
    users[data['username']] = generate_password_hash(data['password'])
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login_user():
    data = request.json
    user = users.get(data['username'])
    if user and check_password_hash(user, data['password']):
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401
