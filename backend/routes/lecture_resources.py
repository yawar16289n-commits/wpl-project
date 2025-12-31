from flask import Blueprint, jsonify, request
from models import LectureResource, CourseModule
from database import db

lecture_resources_bp = Blueprint('lecture_resources', __name__, url_prefix='/lecture-resources')

# Create Lecture Resource (POST)
@lecture_resources_bp.route('/', methods=['POST'])
def create_lecture_resource():
    data = request.get_json()
    
    if not data or 'lecture_id' not in data or 'resource_type' not in data or 'title' not in data:
        return jsonify({
            'success': False,
            'error': 'lecture_id, resource_type, and title are required'
        }), 400
    
    # Check if lecture exists
    lecture = CourseModule.query.get(data['lecture_id'])
    if not lecture:
        return jsonify({
            'success': False,
            'error': 'Lecture not found'
        }), 404
    
    new_resource = LectureResource(
        lecture_id=data['lecture_id'],
        resource_type=data['resource_type'],
        title=data['title'],
        url=data.get('url'),
        content=data.get('content'),
        duration=data.get('duration'),
        order=data.get('order', 0)
    )
    
    db.session.add(new_resource)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Lecture resource created successfully',
        'resource': new_resource.to_dict()
    }), 201


# Get All Lecture Resources (GET)
@lecture_resources_bp.route('/', methods=['GET'])
def get_all_lecture_resources():
    lecture_id = request.args.get('lecture_id')
    
    if lecture_id:
        resources = LectureResource.query.filter_by(
            lecture_id=lecture_id,
            status='active'
        ).order_by(LectureResource.order).all()
    else:
        resources = LectureResource.query.filter_by(
            status='active'
        ).order_by(LectureResource.lecture_id, LectureResource.order).all()
    
    return jsonify({
        'success': True,
        'resources': [resource.to_dict() for resource in resources]
    }), 200


# Get Lecture Resource by ID (GET)
@lecture_resources_bp.route('/<int:resource_id>', methods=['GET'])
def get_lecture_resource(resource_id):
    resource = LectureResource.query.get(resource_id)
    
    if not resource:
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    return jsonify({
        'success': True,
        'resource': resource.to_dict()
    }), 200


# Update Lecture Resource (PUT)
@lecture_resources_bp.route('/<int:resource_id>', methods=['PUT'])
def update_lecture_resource(resource_id):
    resource = LectureResource.query.get(resource_id)
    
    if not resource:
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    data = request.get_json()
    
    if 'title' in data:
        resource.title = data['title']
    if 'resource_type' in data:
        resource.resource_type = data['resource_type']
    if 'url' in data:
        resource.url = data['url']
    if 'content' in data:
        resource.content = data['content']
    if 'duration' in data:
        resource.duration = data['duration']
    if 'order' in data:
        resource.order = data['order']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Resource updated successfully',
        'resource': resource.to_dict()
    }), 200


# Delete Lecture Resource (DELETE)
@lecture_resources_bp.route('/<int:resource_id>', methods=['DELETE'])
def delete_lecture_resource(resource_id):
    resource = LectureResource.query.get(resource_id)
    
    if not resource:
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    # Soft delete: set status to deleted
    resource.status = 'deleted'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Resource deleted successfully'
    }), 200
