from flask import Blueprint, jsonify, request
from models import User, Course, Enrollment, Progress
from database import db
from datetime import datetime

enrollments_bp = Blueprint('enrollments', __name__, url_prefix='/enrollments')


# Create Enrollment (POST)
@enrollments_bp.route('/', methods=['POST'])
def enroll_in_course():
    from routes.progress import initialize_progress_for_enrollment
    
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'course_id' not in data:
        return jsonify({
            'success': False,
            'error': 'user_id and course_id are required'
        }), 400
    
    user_id = data['user_id']
    course_id = data['course_id']
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    if user.role == 'instructor':
        return jsonify({'success': False, 'error': 'Instructors cannot enroll in courses'}), 403
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'success': False, 'error': 'Course not found'}), 404
    
    if course.status != 'active':
        return jsonify({'success': False, 'error': 'Course is not available for enrollment'}), 400
    
    existing_enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        if existing_enrollment.status in ['dropped', 'deleted']:
            existing_enrollment.status = 'active'
            existing_enrollment.enrolled_at = datetime.utcnow()
            db.session.commit()
            # Initialize progress rows again for re-enrollment
            initialize_progress_for_enrollment(existing_enrollment.id)
            
            return jsonify({
                'success': True,
                'message': 'Re-enrolled in course successfully',
                'enrollment': existing_enrollment.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Already enrolled in this course'
            }), 400
    
    # Create new enrollment
    new_enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        status='active',
        enrolled_at=datetime.utcnow()
    )
    
    db.session.add(new_enrollment)
    db.session.commit()
    
    # Automatically create progress rows for all lectures
    initialize_progress_for_enrollment(new_enrollment.id)
    
    return jsonify({
        'success': True,
        'message': 'Enrolled in course successfully',
        'enrollment': new_enrollment.to_dict()
    }), 201


# --- Get All Enrollments ---
@enrollments_bp.route('/', methods=['GET'])
def get_all_enrollments():
    user_id = request.args.get('user_id')
    course_id = request.args.get('course_id')
    status = request.args.get('status')

    query = Enrollment.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if status:
        query = query.filter_by(status=status)

    enrollments = query.all()
    return jsonify({'success': True, 'enrollments': [e.to_dict(include_course=True) for e in enrollments], 'total': len(enrollments)}), 200


# --- Get Enrollment by ID ---
@enrollments_bp.route('/<int:enrollment_id>', methods=['GET'])
def get_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'success': False, 'error': 'Enrollment not found'}), 404
    return jsonify({'success': True, 'enrollment': enrollment.to_dict(include_course=True)}), 200


# --- Delete / Unenroll ---
@enrollments_bp.route('/<int:enrollment_id>', methods=['DELETE'])
def unenroll_from_course(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'success': False, 'error': 'Enrollment not found'}), 404

    if enrollment.status in ['deleted', 'dropped']:
        return jsonify({'success': False, 'error': 'Already unenrolled'}), 400

    enrollment.status = 'deleted'
    Progress.query.filter_by(enrollment_id=enrollment.id).update({'status': 'deleted'})
    db.session.commit()
    return jsonify({'success': True, 'message': 'Unenrolled successfully'}), 200


# --- Get User Enrollments ---
@enrollments_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_enrollments(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    enrollments = Enrollment.query.filter(
        Enrollment.user_id == user_id,
        Enrollment.status.in_(['active', 'completed'])
    ).all()

    return jsonify({
        'success': True,
        'enrollments': [e.to_dict(include_course=True) for e in enrollments],
        'total': len(enrollments)
    }), 200


# --- Check if user is enrolled in a course ---
@enrollments_bp.route('/check/<int:user_id>/<int:course_id>', methods=['GET'])
def check_enrollment(user_id, course_id):
    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).filter(
        Enrollment.status.in_(['active', 'completed'])
    ).first()
    
    if enrollment:
        return jsonify({
            'success': True,
            'enrolled': True,
            'enrollment': enrollment.to_dict()
        }), 200
    else:
        return jsonify({
            'success': True,
            'enrolled': False
        }), 200
