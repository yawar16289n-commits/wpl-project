from flask import Blueprint, jsonify, request
from models import CourseModule
from database import db

lectures_bp = Blueprint('lectures', __name__, url_prefix='/lectures')

# Create Lecture (POST)
@lectures_bp.route('/', methods=['POST'])
def create_lecture():
    data = request.get_json()
    
    if not data or 'course_id' not in data or 'title' not in data or 'number' not in data:
        return jsonify({
            'success': False,
            'error': 'course_id, title, and number are required'
        }), 400
    
    # Check if course exists
    from models import Course
    course = Course.query.get(data['course_id'])
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404
    
    new_lecture = CourseModule(
        course_id=data['course_id'],
        number=data['number'],
        title=data['title'],
        lessons=data.get('lessons', 0),
        duration=data.get('duration')
    )
    
    db.session.add(new_lecture)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Lecture created successfully',
        'lecture': new_lecture.to_dict()
    }), 201


# Get All Lectures (GET)
@lectures_bp.route('/', methods=['GET'])
def get_all_lectures():
    course_id = request.args.get('course_id')
    
    if course_id:
        lectures = CourseModule.query.filter_by(course_id=course_id).order_by(CourseModule.number).all()
    else:
        lectures = CourseModule.query.order_by(CourseModule.course_id, CourseModule.number).all()
    
    return jsonify({
        'success': True,
        'lectures': [lecture.to_dict() for lecture in lectures]
    }), 200


# Get Lecture by ID (GET)
@lectures_bp.route('/<int:lecture_id>', methods=['GET'])
def get_lecture(lecture_id):
    lecture = CourseModule.query.get(lecture_id)
    
    if not lecture:
        return jsonify({
            'success': False,
            'error': 'Lecture not found'
        }), 404
    
    return jsonify({
        'success': True,
        'lecture': lecture.to_dict()
    }), 200


# Update Lecture (PUT)
@lectures_bp.route('/<int:lecture_id>', methods=['PUT'])
def update_lecture(lecture_id):
    lecture = CourseModule.query.get(lecture_id)
    
    if not lecture:
        return jsonify({
            'success': False,
            'error': 'Lecture not found'
        }), 404
    
    data = request.get_json()
    
    if 'title' in data:
        lecture.title = data['title']
    if 'number' in data:
        lecture.number = data['number']
    if 'lessons' in data:
        lecture.lessons = data['lessons']
    if 'duration' in data:
        lecture.duration = data['duration']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Lecture updated successfully',
        'lecture': lecture.to_dict()
    }), 200


# Delete Lecture (DELETE)
@lectures_bp.route('/<int:lecture_id>', methods=['DELETE'])
def delete_lecture(lecture_id):
    lecture = CourseModule.query.get(lecture_id)
    
    if not lecture:
        return jsonify({
            'success': False,
            'error': 'Lecture not found'
        }), 404
    
    db.session.delete(lecture)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Lecture deleted successfully'
    }), 200
