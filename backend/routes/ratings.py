from flask import Blueprint, jsonify, request
from database import db
from models import Rating

ratings_bp = Blueprint('ratings', __name__, url_prefix='/ratings')

# Create Rating (POST)
@ratings_bp.route('/', methods=['POST'])
def create_rating():
    data = request.get_json()
    
    if not data or 'course_id' not in data or 'user_id' not in data or 'rating' not in data:
        return jsonify({
            'success': False,
            'error': 'course_id, user_id, and rating are required'
        }), 400
    
    # Validate rating value
    rating_value = data['rating']
    if not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
        return jsonify({
            'success': False,
            'error': 'Rating must be between 1 and 5'
        }), 400
    
    # Check if user already rated this course
    existing_rating = Rating.query.filter_by(user_id=data['user_id'], course_id=data['course_id']).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating_value
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating updated successfully',
            'rating': existing_rating.to_dict()
        }), 200
    
    # Create new rating
    new_rating = Rating(
        course_id=data['course_id'],
        user_id=data['user_id'],
        rating=rating_value
    )
    
    db.session.add(new_rating)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Rating created successfully',
        'rating': new_rating.to_dict()
    }), 201

# Get User's Ratings (GET)
@ratings_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_ratings(user_id):
    course_id = request.args.get('course_id')
    
    if course_id:
        rating = Rating.query.filter_by(
            user_id=user_id,
            course_id=int(course_id),
            status='active'
        ).first()
        return jsonify({
            'success': True,
            'rating': rating.to_dict() if rating else None
        }), 200
    
    ratings = Rating.query.filter_by(
        user_id=user_id,
        status='active'
    ).all()
    
    return jsonify({
        'success': True,
        'ratings': [rating.to_dict() for rating in ratings]
    }), 200


# Get Average Rating for Course (GET)
@ratings_bp.route('/course/<int:course_id>/average', methods=['GET'])
def get_average_rating(course_id):
    from models import Course
    from sqlalchemy import func
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404
    
    # Calculate average rating from Rating table
    rating_stats = db.session.query(
        func.avg(Rating.rating).label('avg_rating'),
        func.count(Rating.id).label('total_ratings')
    ).filter(
        Rating.course_id == course_id,
        Rating.status == 'active'
    ).first()
    
    avg_rating = float(rating_stats.avg_rating) if rating_stats.avg_rating else 0.0
    total_ratings = rating_stats.total_ratings or 0
    
    return jsonify({
        'success': True,
        'course_id': course_id,
        'average_rating': round(avg_rating, 1),
        'total_ratings': total_ratings
    }), 200


# Delete Rating (DELETE)
@ratings_bp.route('/<int:rating_id>', methods=['DELETE'])
def delete_rating(rating_id):
    rating = Rating.query.get(rating_id)
    if not rating:
        return jsonify({
            'success': False,
            'error': 'Rating not found'
        }), 404
    
    rating.status = 'deleted'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Rating deleted successfully'
    }), 200
