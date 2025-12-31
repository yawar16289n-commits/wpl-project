from flask import Blueprint, jsonify, request
from models import Course
from database import db

course_categories_bp = Blueprint('course_categories', __name__, url_prefix='/course-categories')

# Get All Categories (GET)
@course_categories_bp.route('/', methods=['GET'])
def get_all_categories():
    # Get distinct categories from courses
    categories = db.session.query(Course.category).distinct().all()
    
    category_list = [cat[0] for cat in categories if cat[0]]
    
    return jsonify({
        'success': True,
        'categories': category_list
    }), 200


# Get Category by Name (GET)
@course_categories_bp.route('/<string:category_name>', methods=['GET'])
def get_category(category_name):
    courses = Course.query.filter_by(category=category_name).all()
    
    if not courses:
        return jsonify({
            'success': False,
            'error': 'Category not found or has no courses'
        }), 404
    
    return jsonify({
        'success': True,
        'category': category_name,
        'courses': [course.to_dict() for course in courses],
        'total_courses': len(courses)
    }), 200


# Get Courses by Category (GET)
@course_categories_bp.route('/<string:category_name>/courses', methods=['GET'])
def get_courses_by_category(category_name):
    courses = Course.query.filter_by(category=category_name, status='active').all()
    
    return jsonify({
        'success': True,
        'category': category_name,
        'courses': [course.to_dict(include_instructor=True) for course in courses],
        'total_courses': len(courses)
    }), 200


# Get Category Statistics (GET)
@course_categories_bp.route('/<string:category_name>/stats', methods=['GET'])
def get_category_stats(category_name):
    from models import Enrollment, Rating
    from sqlalchemy import func
    
    courses = Course.query.filter_by(category=category_name).all()
    
    if not courses:
        return jsonify({
            'success': False,
            'error': 'Category not found'
        }), 404
    
    course_ids = [course.id for course in courses]
    
    # Calculate total students from active enrollments
    total_students = Enrollment.query.filter(
        Enrollment.course_id.in_(course_ids),
        Enrollment.status.in_(['active', 'completed'])
    ).distinct(Enrollment.user_id).count()
    
    # Calculate average rating from ratings
    avg_rating_result = db.session.query(func.avg(Rating.rating)).filter(
        Rating.course_id.in_(course_ids),
        Rating.status == 'active'
    ).scalar()
    
    avg_rating = float(avg_rating_result) if avg_rating_result else 0.0
    
    return jsonify({
        'success': True,
        'category': category_name,
        'stats': {
            'total_courses': len(courses),
            'total_students': total_students,
            'average_rating': round(avg_rating, 1)
        }
    }), 200
