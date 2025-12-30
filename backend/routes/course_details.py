from flask import Blueprint, jsonify, request
from models import Course
from database import db
from middleware.auth import require_owner

course_details_bp = Blueprint('course_details', __name__, url_prefix='/course-details')

# Create Course Details (POST)
@course_details_bp.route('/', methods=['POST'])
def create_course_details():
    data = request.get_json()
    
    if not data or 'course_id' not in data:
        return jsonify({
            'success': False,
            'error': 'course_id is required'
        }), 400
    
    course = Course.query.get(data['course_id'])
    
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404
    
    # Update course details
    if 'about' in data:
        course.about = data['about']
    if 'learning_outcomes' in data:
        import json
        course.learning_outcomes = json.dumps(data['learning_outcomes'])
    if 'skills' in data:
        import json
        course.skills = json.dumps(data['skills'])
    if 'language' in data:
        course.language = data['language']
    if 'subtitles' in data:
        import json
        course.subtitles = json.dumps(data['subtitles'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course details created successfully',
        'course_details': course.to_dict()
    }), 201


# Get Course Details by ID (GET)
@course_details_bp.route('/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    course = Course.query.get(course_id)
    
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course details not found'
        }), 404
    
    return jsonify({
        'success': True,
        'course_details': course.to_dict(include_instructor=True, include_modules=True)
    }), 200


# Update Course Details (PUT)
@course_details_bp.route('/<int:course_id>', methods=['PUT'])
def update_course_details(course_id):
    course = Course.query.get(course_id)
    
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course details not found'
        }), 404
    
    data = request.get_json()
    
    if 'about' in data:
        course.about = data['about']
    if 'learning_outcomes' in data:
        import json
        course.learning_outcomes = json.dumps(data['learning_outcomes'])
    if 'skills' in data:
        import json
        course.skills = json.dumps(data['skills'])
    if 'language' in data:
        course.language = data['language']
    if 'subtitles' in data:
        import json
        course.subtitles = json.dumps(data['subtitles'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course details updated successfully',
        'course_details': course.to_dict()
    }), 200


# Delete Course Details (DELETE)
@course_details_bp.route('/<int:course_id>', methods=['DELETE'])
def delete_course_details(course_id):
    course = Course.query.get(course_id)
    
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course details not found'
        }), 404
    
    # Reset course details fields
    course.about = None
    course.learning_outcomes = None
    course.skills = None
    course.subtitles = None
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course details deleted successfully'
    }), 200
