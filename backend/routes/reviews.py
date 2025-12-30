from flask import Blueprint, jsonify, request
from database import db
from models import Review, User, Course

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

# Create Review (POST)
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
    
    # Verify course exists
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404
    
    # Verify user exists
    if not user:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404
    
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


# Get Reviews for Course (GET)
@reviews_bp.route('/course/<int:course_id>', methods=['GET'])
def get_course_reviews(course_id):
    reviews = Review.query.filter_by(course_id=course_id).all()
    
    return jsonify({
        'success': True,
        'reviews': [review.to_dict(include_user=True) for review in reviews]
    }), 200


# Get All Reviews (GET)
@reviews_bp.route('/', methods=['GET'])
def get_all_reviews():
    reviews = Review.query.all()
    
    return jsonify({
        'success': True,
        'reviews': [review.to_dict(include_user=True) for review in reviews]
    }), 200


# Get Review by ID (GET)
@reviews_bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({
            'success': False,
            'error': 'Review not found'
        }), 404
    
    return jsonify({
        'success': True,
        'review': review.to_dict(include_user=True)
    }), 200


# Update Review (PUT)
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


# Delete Review (DELETE)
@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({
            'success': False,
            'error': 'Review not found'
        }), 404
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Review deleted successfully'
    }), 200
