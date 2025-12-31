from flask import Blueprint, jsonify, request
from models import User, Course, Enrollment, LectureResource, CourseModule, Progress
from database import db
from datetime import datetime

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')


def initialize_progress_for_enrollment(enrollment_id):
    """Create Progress rows for all lectures in the course for a new enrollment"""
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return

    lectures = LectureResource.query.join(
        CourseModule, LectureResource.lecture_id == CourseModule.id
    ).filter(
        CourseModule.course_id == enrollment.course_id,
        LectureResource.status == 'active',
        CourseModule.status == 'active'
    ).all()

    for lecture in lectures:
        progress = Progress(
            enrollment_id=enrollment_id,
            lecture_resource_id=lecture.id,
            completed=False,
            status='active'
        )
        db.session.add(progress)
    
    db.session.commit()


# Mark Lecture Resource as Complete
@progress_bp.route('/complete', methods=['POST'])
def mark_lecture_complete():
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
        progress.completed = True
        progress.completed_at = datetime.utcnow()
    else:
        # Create progress if it doesn't exist (should normally exist)
        progress = Progress(
            enrollment_id=enrollment_id,
            lecture_resource_id=lecture_resource.id,
            completed=True,
            completed_at=datetime.utcnow(),
            status='active'
        )
        db.session.add(progress)

    # Update course completion if all lectures completed
    total_lectures = Progress.query.filter_by(enrollment_id=enrollment_id, status='active').count()
    completed_lectures = Progress.query.filter_by(enrollment_id=enrollment_id, completed=True, status='active').count()
    course_progress = int((completed_lectures / total_lectures) * 100) if total_lectures else 0

    if course_progress >= 100:
        enrollment.status = 'completed'
        enrollment.completed_at = datetime.utcnow()
    else:
        enrollment.status = 'active'
        enrollment.completed_at = None

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Lecture marked as complete',
        'progress': {
            'lecture_resource_id': lecture_resource.id,
            'completed': True,
            'course_progress': course_progress,
            'enrollment_id': enrollment_id
        }
    }), 200


# Mark Lecture Resource as Uncomplete
@progress_bp.route('/uncomplete', methods=['POST'])
def mark_lecture_uncomplete():
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
        progress.completed = False
        progress.completed_at = None
    else:
        # Create progress if it doesn't exist
        progress = Progress(
            enrollment_id=enrollment_id,
            lecture_resource_id=lecture_resource.id,
            completed=False,
            status='active'
        )
        db.session.add(progress)

    # Update enrollment status
    total_lectures = Progress.query.filter_by(enrollment_id=enrollment_id, status='active').count()
    completed_lectures = Progress.query.filter_by(enrollment_id=enrollment_id, completed=True, status='active').count()
    course_progress = int((completed_lectures / total_lectures) * 100) if total_lectures else 0

    if course_progress < 100:
        enrollment.status = 'active'
        enrollment.completed_at = None

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Lecture marked as incomplete',
        'progress': {
            'lecture_resource_id': lecture_resource.id,
            'completed': False,
            'course_progress': course_progress,
            'enrollment_id': enrollment_id
        }
    }), 200


# Create Enrollment (POST)
@progress_bp.route('/', methods=['POST'])
def enroll_in_course():
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'course_id' not in data:
        return jsonify({'success': False, 'error': 'user_id and course_id are required'}), 400
    
    user_id = data['user_id']
    course_id = data['course_id']
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    if user.role == 'instructor':
        return jsonify({'success': False, 'error': 'Instructors cannot enroll in courses'}), 403
    
    course = Course.query.get(course_id)
    if not course or course.status != 'active':
        return jsonify({'success': False, 'error': 'Course not available'}), 404
    
    # Always create a new enrollment for re-enrollment
    new_enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        status='active',
        enrolled_at=datetime.utcnow()
    )
    db.session.add(new_enrollment)
    db.session.commit()

    # Initialize progress rows for this enrollment
    initialize_progress_for_enrollment(new_enrollment.id)
    
    return jsonify({
        'success': True,
        'message': 'Enrolled in course successfully',
        'enrollment': new_enrollment.to_dict()
    }), 201


# Get User Enrollments (GET)
@progress_bp.route('/user/<int:user_id>', methods=['GET'])
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
        'enrollments': [
            {
                'enrollment_id': e.id,
                'course_id': e.course_id,
                'progress': e.progress,  # computed from Progress table
                'status': e.status
            } for e in enrollments
        ],
        'total': len(enrollments)
    }), 200


# Unenroll (soft delete)
@progress_bp.route('/<int:enrollment_id>', methods=['DELETE'])
def unenroll(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment or enrollment.status == 'deleted':
        return jsonify({'success': False, 'error': 'Enrollment not found or already deleted'}), 404

    enrollment.status = 'deleted'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Enrollment deleted successfully'}), 200

    return jsonify({'success': True, 'message': 'Progress records deleted'}), 200


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


# Get all completed lectures
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


# Student Dashboard
@progress_bp.route('/dashboard/student/<int:user_id>', methods=['GET'])
def get_student_dashboard(user_id):
    from models import Course, User
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    enrollments = Enrollment.query.filter_by(
        user_id=user_id
    ).filter(
        Enrollment.status.in_(['active', 'completed'])
    ).all()
    
    courses_with_progress = []
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        if not course or course.status != 'active':
            continue
        
        total_lectures = Progress.query.filter_by(enrollment_id=enrollment.id, status='active').count()
        completed_lectures = Progress.query.filter_by(enrollment_id=enrollment.id, completed=True, status='active').count()
        progress_percentage = int((completed_lectures / total_lectures) * 100) if total_lectures else 0
        
        courses_with_progress.append({
            'enrollment_id': enrollment.id,
            'course': course.to_dict(include_instructor=True),
            'progress_percentage': progress_percentage,
            'enrolled_at': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
            'status': enrollment.status
        })
    
    return jsonify({
        'success': True,
        'courses': courses_with_progress,
        'total': len(courses_with_progress)
    }), 200


# Instructor Dashboard
@progress_bp.route('/dashboard/instructor/<int:user_id>', methods=['GET'])
def get_instructor_dashboard(user_id):
    from models import Course, User
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    if user.role != 'instructor':
        return jsonify({'success': False, 'error': 'User is not an instructor'}), 403
    
    courses = Course.query.filter_by(
        instructor_id=user_id
    ).filter(
        Course.status.in_(['active', 'unpublished'])
    ).all()
    
    courses_with_stats = []
    for course in courses:
        total_enrollments = Enrollment.query.filter_by(
            course_id=course.id
        ).filter(
            Enrollment.status.in_(['active', 'completed'])
        ).count()
        
        completed_enrollments = Enrollment.query.filter_by(
            course_id=course.id,
            status='completed'
        ).count()
        
        courses_with_stats.append({
            'course': course.to_dict(include_stats=True),
            'total_students': total_enrollments,
            'completed_students': completed_enrollments,
            'rating': course.rating,
            'total_reviews': course.total_reviews
        })
    
    return jsonify({
        'success': True,
        'courses': courses_with_stats,
        'total': len(courses_with_stats)
    }), 200