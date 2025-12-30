from flask import Blueprint, jsonify, request
from models import User, Course
from database import db
from utils.helpers import get_user_or_404
from middleware.auth import require_owner

users_bp = Blueprint('users', __name__, url_prefix='/users')

# Create User (POST)
@users_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data or 'password' not in data or 'role' not in data:
        return jsonify({
            'success': False,
            'error': 'name, email, password, and role are required'
        }), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({
            'success': False,
            'error': 'User with this email already exists'
        }), 400
    
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        role=data['role'],
        profile_picture=data.get('profile_picture'),
        bio=data.get('bio'),
        created_at=datetime.utcnow()
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User created successfully',
        'user': new_user.to_dict()
    }), 201


# Get All Users (GET)
@users_bp.route('/', methods=['GET'])
def get_all_users():
    role = request.args.get('role')
    
    if role:
        users = User.query.filter_by(role=role).all()
    else:
        users = User.query.all()
    
    return jsonify({
        'success': True,
        'users': [user.to_dict() for user in users]
    }), 200


# Get User by ID (GET)
@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user, error_response, status_code = get_user_or_404(user_id)
    if error_response:
        return error_response, status_code
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200


# Update User (PUT)
@users_bp.route('/<int:user_id>', methods=['PUT'])
@require_owner
def update_user(user_id):
    user, error_response, status_code = get_user_or_404(user_id)
    if error_response:
        return error_response, status_code
    
    data = request.get_json()
    
    if 'name' in data:
        user.name = data['name']
    if 'bio' in data:
        user.bio = data['bio']
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']
    if 'email' in data:
        # Check if email is already taken
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({
                'success': False,
                'error': 'Email already in use'
            }), 400
        user.email = data['email']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200


# Delete User (DELETE)
@users_bp.route('/<int:user_id>', methods=['DELETE'])
@require_owner
def delete_user(user_id):
    user, error_response, status_code = get_user_or_404(user_id)
    if error_response:
        return error_response, status_code
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User deleted successfully'
    }), 200


# Legacy profile routes
@users_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_public_profile(user_id):
    user, error_response, status_code = get_user_or_404(user_id)
    if error_response:
        return error_response, status_code
    
    profile = {
        'id': user.id,
        'name': user.name,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'role': user.role
    }
    
    if user.role == 'instructor':
        created_courses = Course.query.filter_by(instructor_id=user_id, is_published=True).all()
        profile['courses'] = [course.to_dict() for course in created_courses]
        profile['total_courses'] = len(created_courses)
    
    return jsonify({
        'success': True,
        'profile': profile
    }), 200


@users_bp.route('/my-profile/<int:user_id>', methods=['GET'])
@require_owner
def get_my_profile(user_id):
    user, error_response, status_code = get_user_or_404(user_id)
    if error_response:
        return error_response, status_code
    
    profile = user.to_dict()
    
    return jsonify({
        'success': True,
        'profile': profile
    }), 200

@users_bp.route('/profile/<int:user_id>', methods=['PUT'])
@require_owner
def update_profile(user_id):
    user, error_response, status_code = get_user_or_404(user_id)
    if error_response:
        return error_response, status_code
    
    data = request.get_json()
    
    if 'name' in data:
        user.name = data['name']
    if 'bio' in data:
        user.bio = data['bio']
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully',
        'profile': user.to_dict()
    }), 200


# Authentication Endpoints (migrated from auth.py)
@users_bp.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data or 'password' not in data or 'role' not in data:
        return jsonify({
            'success': False,
            'error': 'name, email, password, and role are required'
        }), 400
    
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({
            'success': False,
            'error': 'User with this email already exists'
        }), 400
    
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        role=data['role'],
        profile_picture=data.get('profile_picture'),
        bio=data.get('bio'),
        created_at=datetime.utcnow()
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User created successfully',
        'user': new_user.to_dict()
    }), 201


@users_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'error': 'email and password are required'
        }), 400
    
    from werkzeug.security import check_password_hash
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({
            'success': False,
            'error': 'Invalid email or password'
        }), 401
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200
