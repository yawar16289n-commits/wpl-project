from flask import Blueprint, jsonify, request
from models import User
from database import db
from middleware.auth import require_owner
from datetime import datetime

users_bp = Blueprint('users', __name__, url_prefix='/users')

# ----------------------
# Helpers
# ----------------------
def user_not_found():
    return jsonify({'success': False, 'error': 'User not found'}), 404

def get_user(user_id):
    return User.query.get(user_id)

def json_response(success=True, **kwargs):
    return jsonify({'success': success, **kwargs})

# ----------------------
# Create User / Signup
# ----------------------
def create_user_helper(data):
    required = ['name', 'email', 'password', 'role']
    if any(k not in data for k in required):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'error': 'Email already exists'}), 400

    user = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        role=data['role'],
        created_at=datetime.utcnow()
    )
    db.session.add(user)
    db.session.commit()

    return json_response(message='User created successfully', user=user.to_dict()), 201

@users_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    return create_user_helper(data)

@users_bp.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    return create_user_helper(data)

# ----------------------
# Login
# ----------------------
@users_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or user.password != data['password']:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    return json_response(message='Login successful', user=user.to_dict())

# ----------------------
# Get Users
# ----------------------
@users_bp.route('/', methods=['GET'])
def get_all_users():
    role = request.args.get('role')
    users = User.query.filter_by(role=role).all() if role else User.query.all()
    return json_response(users=[u.to_dict() for u in users])

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = get_user(user_id)
    if not user: return user_not_found()
    return json_response(user=user.to_dict())

# ----------------------
# Update User
# ----------------------
@users_bp.route('/<int:user_id>', methods=['PUT'])
@require_owner
def update_user(user_id):
    user = get_user(user_id)
    if not user: return user_not_found()

    data = request.get_json()
    if 'name' in data: user.name = data['name']
    if 'email' in data:
        if User.query.filter(User.email==data['email'], User.id!=user_id).first():
            return jsonify({'success': False, 'error': 'Email already in use'}), 400
        user.email = data['email']

    db.session.commit()
    return json_response(message='User updated successfully', user=user.to_dict())

# ----------------------
# Delete User (Soft Delete)
# ----------------------
@users_bp.route('/<int:user_id>', methods=['DELETE'])
@require_owner
def delete_user(user_id):
    user = get_user(user_id)
    if not user: return user_not_found()

    # Soft delete - set status to 'deleted'
    user.status = 'deleted'
    db.session.commit()
    return json_response(message='User deleted successfully')
