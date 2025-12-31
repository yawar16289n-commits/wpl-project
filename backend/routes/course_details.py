from flask import Blueprint, jsonify, request
from models import Course, CourseDetail
from database import db
from middleware.auth import require_owner
import json

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
    
    # Check if details already exist
    existing_details = CourseDetail.query.filter_by(course_id=course.id).first()
    if existing_details:
        return jsonify({
            'success': False,
            'error': 'Course details already exist'
        }), 409
    
    # Create course details
    course_detail = CourseDetail(
        course_id=course.id,
        skills=json.dumps(data.get('skills', [])) if data.get('skills') else None,
        requirements=json.dumps(data.get('requirements', [])) if data.get('requirements') else None,
        who_is_for=json.dumps(data.get('who_is_for', [])) if data.get('who_is_for') else None,
        objectives=json.dumps(data.get('objectives', [])) if data.get('objectives') else None,
        status='active'
    )
    
    db.session.add(course_detail)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course details created successfully',
        'course_details': course_detail.to_dict()
    }), 201


# Get Course Details by ID (GET)
@course_details_bp.route('/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    course_detail = CourseDetail.query.filter_by(course_id=course_id).first()
    
    if not course_detail:
        return jsonify({
            'success': False,
            'error': 'Course details not found'
        }), 404
    
    return jsonify({
        'success': True,
        'course_details': course_detail.to_dict()
    }), 200


# Update Course Details (PUT)
@course_details_bp.route('/<int:course_id>', methods=['PUT'])
def update_course_details(course_id):
    course_detail = CourseDetail.query.filter_by(course_id=course_id).first()
    
    if not course_detail:
        return jsonify({
            'success': False,
            'error': 'Course details not found'
        }), 404
    
    data = request.get_json()
    
    if 'skills' in data:
        course_detail.skills = json.dumps(data['skills'])
    if 'requirements' in data:
        course_detail.requirements = json.dumps(data['requirements'])
    if 'who_is_for' in data:
        course_detail.who_is_for = json.dumps(data['who_is_for'])
    if 'objectives' in data:
        course_detail.objectives = json.dumps(data['objectives'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course details updated successfully',
        'course_details': course_detail.to_dict()
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
