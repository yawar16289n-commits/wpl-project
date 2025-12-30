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
    courses = Course.query.filter_by(category=category_name, is_published=True).all()
    
    return jsonify({
        'success': True,
        'category': category_name,
        'courses': [course.to_dict(include_instructor=True) for course in courses],
        'total_courses': len(courses)
    }), 200


# Get Category Statistics (GET)
@course_categories_bp.route('/<string:category_name>/stats', methods=['GET'])
def get_category_stats(category_name):
    courses = Course.query.filter_by(category=category_name).all()
    
    if not courses:
        return jsonify({
            'success': False,
            'error': 'Category not found'
        }), 404
    
    total_students = sum(course.total_students for course in courses)
    avg_rating = sum(float(course.rating) for course in courses) / len(courses) if courses else 0
    
    return jsonify({
        'success': True,
        'category': category_name,
        'stats': {
            'total_courses': len(courses),
            'total_students': total_students,
            'average_rating': round(avg_rating, 2)
        }
    }), 200
