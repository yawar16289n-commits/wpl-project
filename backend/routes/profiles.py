from flask import Blueprint, jsonify, request
from models import User
from database import db
from middleware.auth import require_owner

profiles_bp = Blueprint('profiles', __name__, url_prefix='/profiles')

# Create Profile (POST)
@profiles_bp.route('/', methods=['POST'])
def create_profile():
    data = request.get_json()
    
    if not data or 'user_id' not in data:
        return jsonify({
            'success': False,
            'error': 'user_id is required'
        }), 400
    
    user = User.query.get(data['user_id'])
    
    if not user:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404
    
    # Update profile fields
    if 'bio' in data:
        user.bio = data['bio']
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Profile created successfully',
        'profile': {
            'id': user.id,
            'name': user.name,
            'bio': user.bio,
            'profile_picture': user.profile_picture,
            'role': user.role
        }
    }), 201


# Get Profile by ID (GET)
@profiles_bp.route('/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'error': 'Profile not found'
        }), 404
    
    profile = {
        'id': user.id,
        'name': user.name,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'role': user.role
    }
    
    return jsonify({
        'success': True,
        'profile': profile
    }), 200


# Update Profile (PUT)
@profiles_bp.route('/<int:user_id>', methods=['PUT'])
@require_owner
def update_profile(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'error': 'Profile not found'
        }), 404
    
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
        'profile': {
            'id': user.id,
            'name': user.name,
            'bio': user.bio,
            'profile_picture': user.profile_picture,
            'role': user.role
        }
    }), 200


# Delete Profile (DELETE)
@profiles_bp.route('/<int:user_id>', methods=['DELETE'])
@require_owner
def delete_profile(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'error': 'Profile not found'
        }), 404
    
    # Reset profile fields
    user.bio = None
    user.profile_picture = None
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Profile deleted successfully'
    }), 200


# Get All Profiles (GET)
@profiles_bp.route('/', methods=['GET'])
def get_all_profiles():
    users = User.query.all()
    
    profiles = [{
        'id': user.id,
        'name': user.name,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'role': user.role
    } for user in users]
    
    return jsonify({
        'success': True,
        'profiles': profiles
    }), 200
