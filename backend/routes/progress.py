from flask import Blueprint, jsonify, request
from models import Enrollment
from database import db

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')

# Create Progress (POST)
@progress_bp.route('/', methods=['POST'])
def create_progress():
    data = request.get_json()
    
    if not data or 'enrollment_id' not in data or 'progress' not in data:
        return jsonify({
            'success': False,
            'error': 'enrollment_id and progress are required'
        }), 400
    
    enrollment = Enrollment.query.get(data['enrollment_id'])
    
    if not enrollment:
        return jsonify({
            'success': False,
            'error': 'Enrollment not found'
        }), 404
    
    # Validate progress value
    progress_value = data['progress']
    if not isinstance(progress_value, int) or progress_value < 0 or progress_value > 100:
        return jsonify({
            'success': False,
            'error': 'Progress must be between 0 and 100'
        }), 400
    
    enrollment.progress = progress_value
    
    # Update status if completed
    if progress_value == 100:
        enrollment.status = 'completed'
        from datetime import datetime
        enrollment.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Progress created successfully',
        'progress': {
            'enrollment_id': enrollment.id,
            'user_id': enrollment.user_id,
            'course_id': enrollment.course_id,
            'progress': enrollment.progress,
            'status': enrollment.status
        }
    }), 201


# Get All Progress (GET)
@progress_bp.route('/', methods=['GET'])
def get_all_progress():
    user_id = request.args.get('user_id')
    course_id = request.args.get('course_id')
    
    query = Enrollment.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    
    enrollments = query.all()
    
    progress_list = [{
        'enrollment_id': e.id,
        'user_id': e.user_id,
        'course_id': e.course_id,
        'progress': e.progress,
        'status': e.status
    } for e in enrollments]
    
    return jsonify({
        'success': True,
        'progress': progress_list
    }), 200


# Get Progress by Enrollment ID (GET)
@progress_bp.route('/<int:enrollment_id>', methods=['GET'])
def get_progress(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    
    if not enrollment:
        return jsonify({
            'success': False,
            'error': 'Progress not found'
        }), 404
    
    return jsonify({
        'success': True,
        'progress': {
            'enrollment_id': enrollment.id,
            'user_id': enrollment.user_id,
            'course_id': enrollment.course_id,
            'progress': enrollment.progress,
            'status': enrollment.status,
            'enrolled_at': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
            'completed_at': enrollment.completed_at.isoformat() if enrollment.completed_at else None
        }
    }), 200


# Update Progress (PUT)
@progress_bp.route('/<int:enrollment_id>', methods=['PUT'])
def update_progress(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    
    if not enrollment:
        return jsonify({
            'success': False,
            'error': 'Progress not found'
        }), 404
    
    data = request.get_json()
    
    if 'progress' in data:
        progress_value = data['progress']
        
        # Validate progress value
        if not isinstance(progress_value, int) or progress_value < 0 or progress_value > 100:
            return jsonify({
                'success': False,
                'error': 'Progress must be between 0 and 100'
            }), 400
        
        enrollment.progress = progress_value
        
        # Update status if completed
        if progress_value == 100:
            enrollment.status = 'completed'
            from datetime import datetime
            enrollment.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Progress updated successfully',
        'progress': {
            'enrollment_id': enrollment.id,
            'user_id': enrollment.user_id,
            'course_id': enrollment.course_id,
            'progress': enrollment.progress,
            'status': enrollment.status
        }
    }), 200


# Delete Progress (DELETE)
@progress_bp.route('/<int:enrollment_id>', methods=['DELETE'])
def delete_progress(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    
    if not enrollment:
        return jsonify({
            'success': False,
            'error': 'Progress not found'
        }), 404
    
    # Reset progress
    enrollment.progress = 0
    enrollment.status = 'active'
    enrollment.completed_at = None
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Progress reset successfully'
    }), 200


# Dashboard Endpoints (migrated from dashboard.py)
@progress_bp.route('/dashboard/student/<int:user_id>', methods=['GET'])
def get_student_dashboard(user_id):
    from models import User, Course
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404
    
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    
    in_progress = []
    completed = []
    
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        if course:
            enrollment_data = {
                'id': enrollment.id,
                'user_id': enrollment.user_id,
                'course_id': enrollment.course_id,
                'progress': enrollment.progress,
                'status': enrollment.status,
                'enrolled_at': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
                'completed_at': enrollment.completed_at.isoformat() if enrollment.completed_at else None,
                'course': course.to_dict(include_instructor=True)
            }
            
            if enrollment.status == 'completed':
                completed.append(enrollment_data)
            else:
                in_progress.append(enrollment_data)
    
    return jsonify({
        'success': True,
        'dashboard': {
            'user': user.to_dict(),
            'enrolled_courses': {
                'in_progress': in_progress,
                'completed': completed
            },
            'stats': {
                'total_enrolled': len(enrollments),
                'in_progress': len(in_progress),
                'completed': len(completed),
                'average_progress': sum(e.progress for e in enrollments) // len(enrollments) if enrollments else 0
            }
        }
    }), 200


@progress_bp.route('/dashboard/instructor/<int:user_id>', methods=['GET'])
def get_instructor_dashboard(user_id):
    from models import User, Course
    
    user = User.query.get(user_id)
    if not user or user.role != 'instructor':
        return jsonify({
            'success': False,
            'error': 'Instructor not found'
        }), 404
    
    courses = Course.query.filter_by(instructor_id=user_id).all()
    
    published = []
    drafts = []
    total_students = 0
    total_rating = 0
    
    for course in courses:
        enrollments = Enrollment.query.filter_by(course_id=course.id).all()
        total_students += len(enrollments)
        total_rating += float(course.rating) if course.rating else 0
        
        course_data = course.to_dict()
        course_data['enrollments'] = len(enrollments)
        course_data['completed_students'] = len([e for e in enrollments if e.status == 'completed'])
        
        if course.is_published:
            published.append(course_data)
        else:
            drafts.append(course_data)
    
    return jsonify({
        'success': True,
        'dashboard': {
            'user': user.to_dict(),
            'created_courses': {
                'published': published,
                'drafts': drafts
            },
            'stats': {
                'total_courses': len(courses),
                'published': len(published),
                'drafts': len(drafts),
                'total_students': total_students,
                'average_rating': total_rating / len(courses) if courses else 0
            }
        }
    }), 200
