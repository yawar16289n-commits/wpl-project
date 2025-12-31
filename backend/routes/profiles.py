from flask import Blueprint, jsonify, request
from models import User, Profile, Course
from database import db
from middleware.auth import require_owner
import json

profiles_bp = Blueprint('profiles', __name__, url_prefix='/profiles')

# ----------------------
# Helpers
# ----------------------
def get_user(user_id):
    return User.query.get(user_id)

def user_not_found():
    return jsonify({'success': False, 'error': 'User not found'}), 404

def get_or_create_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id, status='active')
        db.session.add(profile)
    return profile

def json_response(success=True, **kwargs):
    return jsonify({'success': success, **kwargs})

# ----------------------
# Create Profile
# ----------------------
@profiles_bp.route('/', methods=['POST'])
def create_profile():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'success': False, 'error': 'user_id required'}), 400

    user = get_user(data['user_id'])
    if not user or user.status != 'active': return user_not_found()

    if Profile.query.filter_by(user_id=user.id).first():
        return jsonify({'success': False, 'error': 'Profile already exists'}), 409

    profile = Profile(
        user_id=user.id,
        bio=data.get('bio'),
        profile_picture=data.get('profile_picture'),
        website=data.get('website'),
        social_links=json.dumps(data.get('social_links', [])),
        expertise=json.dumps(data.get('expertise', [])),
        education=json.dumps(data.get('education', [])),
        status='active'
    )

    db.session.add(profile)
    db.session.commit()

    return json_response(message='Profile created successfully', profile={
        'id': user.id,
        'name': user.name,
        'role': user.role,
        'bio': profile.bio,
        'profile_picture': profile.profile_picture
    }), 201

# ----------------------
# Get Profile
# ----------------------
@profiles_bp.route('/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = get_user(user_id)
    if not user or user.status != 'active': return user_not_found()
    
    profile = Profile.query.filter_by(user_id=user.id).first()
    data = {
        'id': user.id,
        'name': user.name,
        'role': user.role,
        'bio': profile.bio if profile else None,
        'profile_picture': profile.profile_picture if profile else None
    }
    
    # If instructor, add their courses
    if user.role == 'instructor':
        courses = Course.query.filter_by(instructor_id=user_id, status='active').all()
        data['courses'] = [c.to_dict() for c in courses]
        data['total_courses'] = len(courses)
    
    return json_response(profile=data)

# ----------------------
# Get My Profile (includes full data)
# ----------------------
@profiles_bp.route('/my-profile/<int:user_id>', methods=['GET'])
@require_owner
def get_my_profile(user_id):
    user = get_user(user_id)
    if not user: return user_not_found()
    return json_response(profile=user.to_dict(include_profile=True))

# ----------------------
# Update Profile
# ----------------------
@profiles_bp.route('/<int:user_id>', methods=['PUT'])
@require_owner
def update_profile(user_id):
    user = get_user(user_id)
    if not user or user.status != 'active': return user_not_found()
    
    data = request.get_json()
    if 'name' in data: user.name = data['name']

    profile = get_or_create_profile(user.id)
    for field in ['bio', 'profile_picture', 'website', 'social_links', 'expertise', 'education']:
        if field in data:
            value = json.dumps(data[field]) if field in ['social_links','expertise','education'] else data[field]
            setattr(profile, field, value)

    db.session.commit()
    return json_response(message='Profile updated successfully', profile=user.to_dict(include_profile=True))

# ----------------------
# Delete Profile
# ----------------------
@profiles_bp.route('/<int:user_id>', methods=['DELETE'])
@require_owner
def delete_profile(user_id):
    user = get_user(user_id)
    if not user: return user_not_found()

    profile = Profile.query.filter_by(user_id=user.id).first()
    if profile:
        profile.status = 'deleted'
        db.session.commit()
    
    return json_response(message='Profile deleted successfully')
