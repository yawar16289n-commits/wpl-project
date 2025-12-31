from flask import Blueprint, jsonify, request
from models import Course, User, CourseDetail
from database import db
import json
from datetime import datetime

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

# Create Course (POST)
@courses_bp.route('/', methods=['POST'])
def create_course():
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'description' not in data or 'instructor_id' not in data or 'category' not in data:
            return jsonify({
                'success': False,
                'error': 'title, description, instructor_id, and category are required'
            }), 400
        
        # Verify instructor exists
        instructor = User.query.get(data['instructor_id'])
        if not instructor:
            return jsonify({
                'success': False,
                'error': 'Instructor not found'
            }), 404
        
        if instructor.role != 'instructor':
            return jsonify({
                'success': False,
                'error': 'User is not an instructor'
            }), 400
        
        new_course = Course(
            title=data['title'],
            description=data['description'],
            about=data.get('about'),
            instructor_id=data['instructor_id'],
            company=data.get('company'),
            category=data['category'],
            level=data.get('level', 'Beginner'),
            duration=data.get('duration'),
            image=data.get('image'),
            status=data.get('status', 'unpublished'),
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_course)
        db.session.commit()
        
        # Create CourseDetail if additional fields provided
        if any(key in data for key in ['requirements', 'who_is_for', 'objectives']):
            course_detail = CourseDetail(
                course_id=new_course.id,
                requirements=json.dumps(data.get('requirements', [])) if data.get('requirements') else None,
                who_is_for=json.dumps(data.get('who_is_for', [])) if data.get('who_is_for') else None,
                objectives=json.dumps(data.get('objectives', [])) if data.get('objectives') else None,
                status='active'
            )
            db.session.add(course_detail)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Course created successfully',
            'course': new_course.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating course: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to create course: {str(e)}'
        }), 500


# Get All Courses (GET)
@courses_bp.route('/', methods=['GET'])
def get_all_courses():
    category = request.args.get('category')
    level = request.args.get('level')
    instructor_id = request.args.get('instructor_id')
    status = request.args.get('status')
    
    # Default to showing only active courses for public
    query = Course.query.filter(Course.status != 'deleted')
    
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    if instructor_id:
        query = query.filter_by(instructor_id=instructor_id)
    if status:
        query = query.filter_by(status=status)
    else:
        # If no status specified, only show active courses
        query = query.filter_by(status='active')
    
    courses = query.all()
    
    return jsonify({
        'success': True,
        'courses': [course.to_dict(include_instructor=True) for course in courses]
    }), 200


# Get Course by ID (GET)
@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    from models import Course
    
    course = Course.query.get(course_id)
    
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404
    
    return jsonify({
        'success': True,
        'course': course.to_dict(include_instructor=True, include_modules=True, include_details=True)
    }), 200


# Update Course (PUT)
@courses_bp.route('/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    course = Course.query.get(course_id)
    
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404
    
    data = request.get_json()
    
    if 'title' in data:
        course.title = data['title']
    if 'description' in data:
        course.description = data['description']
    if 'about' in data:
        course.about = data['about']
    if 'company' in data:
        course.company = data['company']
    if 'category' in data:
        course.category = data['category']
    if 'level' in data:
        course.level = data['level']
    if 'duration' in data:
        course.duration = data['duration']
    if 'image' in data:
        course.image = data['image']
    if 'status' in data:
        course.status = data['status']
    
    db.session.commit()
    
    # Update CourseDetail if any detail fields provided
    detail_fields = ['skills', 'requirements', 'who_is_for', 'objectives']
    if any(key in data for key in detail_fields):
        course_detail = CourseDetail.query.filter_by(course_id=course_id).first()
        if not course_detail:
            course_detail = CourseDetail(course_id=course_id, status='active')
            db.session.add(course_detail)
        
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
        'message': 'Course updated successfully',
        'course': course.to_dict()
    }), 200


# Delete Course (DELETE)
@courses_bp.route('/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    course = Course.query.get(course_id)
    
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404
    
    # Soft delete by setting status to 'deleted'
    course.status = 'deleted'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course deleted successfully'
    }), 200


# Search/Filter Courses (migrated from search.py)
@courses_bp.route('/search', methods=['GET'])
def search_courses():
    from models import User
    
    q = request.args.get('q', '')
    category = request.args.get('category', '')
    level = request.args.get('level', '')
    sort = request.args.get('sort', 'created_at')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Only show active courses for public search
    query = Course.query.join(User).filter(Course.status == 'active')
    
    if q:
        pattern = f'%{q}%'
        query = query.filter(
            (Course.title.ilike(pattern)) |
            (Course.description.ilike(pattern)) |
            (User.name.ilike(pattern))
        )
    
    if category:
        query = query.filter(Course.category == category)
    
    if level:
        query = query.filter(Course.level == level)
    
    # Sorting
    if sort == 'title':
        query = query.order_by(Course.title)
    else:
        # Default to newest first
        query = query.order_by(Course.created_at.desc())
    
    paginated = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'success': True,
        'courses': [course.to_dict(include_instructor=True) for course in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

