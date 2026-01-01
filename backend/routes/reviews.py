from flask import Blueprint, jsonify, request
from database import db
from models import Review, User, Course

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@reviews_bp.route('/', methods=['POST'])
def create_review():
    data = request.get_json()
    
    if not data or 'course_id' not in data or 'user_id' not in data or 'comment' not in data:
        return jsonify({
            'success': False,
            'error': 'course_id, user_id, and comment are required'
        }), 400
    
    course = Course.query.get(data['course_id'])
    user = User.query.get(data['user_id'])
    
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404
    
    if not user:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404
    
    if user.role == 'instructor':
        return jsonify({
            'success': False,
            'error': 'Instructors cannot submit reviews'
        }), 403
    
    existing_review = Review.query.filter_by(
        course_id=data['course_id'],
        user_id=data['user_id'],
        status='active'
    ).first()
    
    if existing_review:
        existing_review.comment = data['comment']
        from datetime import datetime
        existing_review.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Review updated successfully',
            'review': existing_review.to_dict(include_user=True)
        }), 200
    
    new_review = Review(
        course_id=data['course_id'],
        user_id=data['user_id'],
        comment=data['comment']
    )
    
    db.session.add(new_review)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Review created successfully',
        'review': new_review.to_dict(include_user=True)
    }), 201


@reviews_bp.route('/course/<int:course_id>', methods=['GET'])
def get_course_reviews(course_id):
    reviews = Review.query.filter_by(
        course_id=course_id,
        status='active'
    ).all()
    
    return jsonify({
        'success': True,
        'reviews': [review.to_dict(include_user=True) for review in reviews]
    }), 200


@reviews_bp.route('/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    data = request.get_json()
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({
            'success': False,
            'error': 'Review not found'
        }), 404
    
    if 'comment' in data:
        review.comment = data['comment']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Review updated successfully',
        'review': review.to_dict(include_user=True)
    }), 200


@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({
            'success': False,
            'error': 'Review not found'
        }), 404
    
    review.status = 'deleted'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Review deleted successfully'
    }), 200
