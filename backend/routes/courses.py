from flask import Blueprint, jsonify, request
from models import Course, User
from database import db

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

# Create Course (POST)
@courses_bp.route('/', methods=['POST'])
def create_course():
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
    
    from datetime import datetime
    import json
    
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
        language=data.get('language', 'English'),
        subtitles=json.dumps(data.get('subtitles', [])) if data.get('subtitles') else None,
        skills=json.dumps(data.get('skills', [])) if data.get('skills') else None,
        learning_outcomes=json.dumps(data.get('learning_outcomes', [])) if data.get('learning_outcomes') else None,
        is_published=data.get('is_published', False),
        created_at=datetime.utcnow()
    )
    
    db.session.add(new_course)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course created successfully',
        'course': new_course.to_dict()
    }), 201


# Get All Courses (GET)
@courses_bp.route('/', methods=['GET'])
def get_all_courses():
    category = request.args.get('category')
    level = request.args.get('level')
    instructor_id = request.args.get('instructor_id')
    is_published = request.args.get('is_published')
    
    query = Course.query
    
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    if instructor_id:
        query = query.filter_by(instructor_id=instructor_id)
    if is_published is not None:
        query = query.filter_by(is_published=is_published.lower() == 'true')
    
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
        'course': course.to_dict(include_instructor=True, include_modules=True)
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
    import json
    
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
    if 'language' in data:
        course.language = data['language']
    if 'subtitles' in data:
        course.subtitles = json.dumps(data['subtitles'])
    if 'skills' in data:
        course.skills = json.dumps(data['skills'])
    if 'learning_outcomes' in data:
        course.learning_outcomes = json.dumps(data['learning_outcomes'])
    if 'is_published' in data:
        course.is_published = data['is_published']
    
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
    
    db.session.delete(course)
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
    
    query = Course.query.join(User)
    
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
    if sort == 'rating':
        query = query.order_by(Course.rating.desc())
    elif sort == 'students':
        query = query.order_by(Course.total_students.desc())
    elif sort == 'title':
        query = query.order_by(Course.title)
    else:
        query = query.order_by(Course.created_at.desc())
    
    paginated = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'success': True,
        'courses': [course.to_dict(include_instructor=True) for course in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

