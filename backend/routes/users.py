from flask import Blueprint, jsonify, request
from models import User
from database import db
from middleware.auth import require_owner
from datetime import datetime

users_bp = Blueprint('users', __name__, url_prefix='/users')

def user_not_found():
    return jsonify({'success': False, 'error': 'User not found'}), 404

def get_user(user_id):
    return User.query.get(user_id)

def json_response(success=True, **kwargs):
    return jsonify({'success': success, **kwargs})

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

@users_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or user.password != data['password']:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    return json_response(message='Login successful', user=user.to_dict())

@users_bp.route('/', methods=['GET'])
def get_all_users():
    # Check if request is from admin with status filter
    admin_id = request.headers.get('X-User-Id')
    status_filter = request.args.get('status')
    
    if status_filter and admin_id:
        admin = User.query.get(int(admin_id))
        if admin and admin.role == 'admin':
            if status_filter == 'all':
                users = User.query.all()
            else:
                users = User.query.filter_by(status=status_filter).all()
            return json_response(users=[u.to_dict() for u in users])
    
    role = request.args.get('role')
    users = User.query.filter_by(role=role).all() if role else User.query.all()
    return json_response(users=[u.to_dict() for u in users])

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = get_user(user_id)
    if not user: return user_not_found()
    return json_response(user=user.to_dict())

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

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    requester_id = request.headers.get('X-User-Id')
    if not requester_id:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    requester = User.query.get(int(requester_id))
    if not requester:
        return jsonify({'success': False, 'error': 'Requester not found'}), 404
    
    if requester.role != 'admin' and requester.id != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    user = get_user(user_id)
    if not user: return user_not_found()
    
    if user.role == 'admin':
        return jsonify({'success': False, 'error': 'Cannot delete admin users'}), 403

    user.status = 'deleted'
    db.session.commit()
    return json_response(message='User deleted successfully')
