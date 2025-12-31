from flask import Blueprint, jsonify, request
from models import User, Course, Enrollment, Progress
from database import db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# =====================================================
# STUDENT DASHBOARD
# =====================================================

@dashboard_bp.route('/student/<int:user_id>', methods=['GET'])
def get_student_dashboard(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    if user.role != 'learner':
        return jsonify({'success': False, 'error': 'User is not a student'}), 403
    
    # Get all enrollments for this student
    enrollments = Enrollment.query.filter_by(user_id=user_id).filter(
        Enrollment.status.in_(['active', 'completed'])
    ).all()
    
    courses_data = []
    for enrollment in enrollments:
        # Fetch course separately since relationship may not be defined
        course = Course.query.get(enrollment.course_id)
        if not course or course.status != 'active':
            continue
        
        # Calculate progress percentage
        total_lectures = Progress.query.filter_by(
            enrollment_id=enrollment.id,
            status='active'
        ).count()
        
        if total_lectures == 0:
            progress_percentage = 0
        else:
            completed_lectures = Progress.query.filter_by(
                enrollment_id=enrollment.id,
                completed=True,
                status='active'
            ).count()
            progress_percentage = int((completed_lectures / total_lectures) * 100)
        
        courses_data.append({
            'enrollment_id': enrollment.id,
            'course': course.to_dict(include_stats=True),
            'progress_percentage': progress_percentage,
            'status': enrollment.status,
            'enrolled_at': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None
        })
    
    return jsonify({
        'success': True,
        'courses': courses_data,
        'total': len(courses_data)
    }), 200


# =====================================================
# INSTRUCTOR DASHBOARD
# =====================================================

@dashboard_bp.route('/instructor/<int:user_id>', methods=['GET'])
def get_instructor_dashboard(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    if user.role != 'instructor':
        return jsonify({'success': False, 'error': 'User is not an instructor'}), 403
    
    # Get all courses created by this instructor
    courses = Course.query.filter_by(
        instructor_id=user_id
    ).filter(
        Course.status.in_(['active', 'unpublished'])
    ).all()
    
    courses_with_stats = []
    for course in courses:
        # Get enrollment stats
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


# =====================================================
# ADMIN DASHBOARD
# =====================================================

@dashboard_bp.route('/admin', methods=['GET'])
def get_admin_dashboard():
    admin_id = request.headers.get('X-User-Id')
    if not admin_id:
        return jsonify({
            'success': False,
            'error': 'Admin authentication required'
        }), 401
    
    user = User.query.get(int(admin_id))
    if not user or user.role != 'admin':
        return jsonify({
            'success': False,
            'error': 'Admin access required'
        }), 403
    
    # Get total active students (learners)
    total_students = User.query.filter_by(role='learner', status='active').count()
    
    # Get total active lecturers (instructors)
    total_lecturers = User.query.filter_by(role='instructor', status='active').count()
    
    # Get total active courses
    total_courses = Course.query.filter_by(status='active').count()
    
    # Get total enrollments (active courses only)
    total_enrollments = Enrollment.query.join(Course).filter(
        Course.status == 'active',
        Enrollment.status == 'active'
    ).count()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_students': total_students,
            'total_lecturers': total_lecturers,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments
        }
    }), 200
