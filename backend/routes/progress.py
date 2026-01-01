from flask import Blueprint, jsonify, request
from models import Enrollment, Progress, LectureResource, CourseModule
from database import db
from datetime import datetime

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')


def initialize_progress_for_enrollment(enrollment_id):
    """Create Progress rows for all lectures for a new enrollment"""
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment or enrollment.status in ['deleted', 'dropped']:
        return  # Do nothing if enrollment is invalid
    
    # Get all active lectures for the course
    lectures = db.session.query(LectureResource).join(
        CourseModule, LectureResource.lecture_id == CourseModule.id
    ).filter(
        CourseModule.course_id == enrollment.course_id,
        LectureResource.status == 'active',
        CourseModule.status == 'active'
    ).all()
    
    for lecture in lectures:
        # Only create if not already exists
        existing = Progress.query.filter_by(
            enrollment_id=enrollment.id,
            lecture_resource_id=lecture.id
        ).first()
        if not existing:
            progress = Progress(
                enrollment_id=enrollment.id,
                lecture_resource_id=lecture.id,
                completed=False,
                status='active'
            )
            db.session.add(progress)
    db.session.commit()


# Toggle Lecture Resource Completion (Complete/Uncomplete)
@progress_bp.route('/toggle', methods=['POST'])
def toggle_lecture_completion():
    data = request.get_json()
    
    # Support both enrollment_id and course_id+user_id
    enrollment_id = data.get('enrollment_id')
    
    if not enrollment_id:
        # Try to find enrollment by course_id and user_id
        course_id = data.get('course_id')
        user_id = data.get('user_id')
        
        if not course_id or not user_id:
            return jsonify({
                'success': False,
                'error': 'Either enrollment_id or (course_id and user_id) are required'
            }), 400
        
        enrollment = Enrollment.query.filter_by(
            course_id=course_id,
            user_id=user_id
        ).filter(
            Enrollment.status.in_(['active', 'completed'])
        ).first()
        
        if not enrollment:
            return jsonify({'success': False, 'error': 'Enrollment not found'}), 404
        
        enrollment_id = enrollment.id
    else:
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment or enrollment.status in ['deleted', 'dropped']:
            return jsonify({'success': False, 'error': 'Enrollment not found'}), 404
    
    if 'lecture_resource_id' not in data:
        return jsonify({'success': False, 'error': 'lecture_resource_id is required'}), 400

    lecture_resource = LectureResource.query.get(data['lecture_resource_id'])
    if not lecture_resource or lecture_resource.status == 'deleted':
        return jsonify({'success': False, 'error': 'Lecture resource not found'}), 404

    progress = Progress.query.filter_by(
        enrollment_id=enrollment_id,
        lecture_resource_id=lecture_resource.id,
        status='active'
    ).first()

    if progress:
        # Toggle completion status
        if progress.completed:
            # Mark as incomplete
            progress.completed = False
            progress.completed_at = None
            message = 'Lecture marked as incomplete'
        else:
            # Mark as complete
            progress.completed = True
            progress.completed_at = datetime.utcnow()
            message = 'Lecture marked as complete'
        
        db.session.add(progress)
    else:
        return jsonify({'success': False, 'error': 'Progress record not found'}), 404

    # Update course completion status
    total_lectures = Progress.query.filter_by(enrollment_id=enrollment_id, status='active').count()
    completed_lectures = Progress.query.filter_by(enrollment_id=enrollment_id, completed=True, status='active').count()
    course_progress = int((completed_lectures / total_lectures) * 100) if total_lectures else 0

    # Update enrollment status based on progress
    if course_progress >= 100:
        enrollment.status = 'completed'
        enrollment.completed_at = datetime.utcnow()
    else:
        enrollment.status = 'active'
        enrollment.completed_at = None

    db.session.commit()

    return jsonify({
        'success': True,
        'message': message,
        'progress': {
            'lecture_resource_id': lecture_resource.id,
            'completed': progress.completed,
            'course_progress': course_progress,
            'enrollment_id': enrollment_id
        }
    }), 200


# Get Course Progress
@progress_bp.route('/course/<int:enrollment_id>', methods=['GET'])
def get_course_progress(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment or enrollment.status in ['deleted', 'dropped']:
        return jsonify({'success': False, 'error': 'Enrollment not found'}), 404

    total_lectures = Progress.query.filter_by(enrollment_id=enrollment.id, status='active').count()
    completed_lectures = Progress.query.filter_by(enrollment_id=enrollment.id, completed=True, status='active').count()
    progress_percentage = int((completed_lectures / total_lectures) * 100) if total_lectures else 0

    return jsonify({
        'success': True,
        'progress': {
            'enrollment_id': enrollment.id,
            'course_id': enrollment.course_id,
            'user_id': enrollment.user_id,
            'progress_percentage': progress_percentage,
            'status': enrollment.status
        }
    }), 200


# Get all completed lectures by enrollment_id
@progress_bp.route('/completed/<int:enrollment_id>', methods=['GET'])
def get_completed_lectures(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({
            'success': False,
            'error': 'Enrollment not found',
            'completed_lectures': []
        }), 404
    
    if enrollment.status in ['deleted', 'dropped']:
        return jsonify({
            'success': True,
            'message': 'Enrollment is not active',
            'completed_lectures': []
        }), 200

    completed = Progress.query.filter_by(enrollment_id=enrollment.id, completed=True, status='active').all()
    completed_list = []
    for p in completed:
        lecture = LectureResource.query.get(p.lecture_resource_id)
        if lecture:
            completed_list.append({
                'lecture_resource_id': lecture.id,
                'title': lecture.title,
                'resource_type': lecture.resource_type,
                'completed_at': p.completed_at.isoformat() if p.completed_at else None
            })

    return jsonify({'success': True, 'completed_lectures': completed_list}), 200

