from flask import Blueprint, jsonify, request
from models import User
from database import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Middleware to check if user is admin
def require_admin(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found', 'status': 404}
    if user.role != 'admin':
        return {'error': 'Admin access required', 'status': 403}
    return None

# =====================================================
# USER MANAGEMENT
# =====================================================

# Get All Users (Admin Only)
@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    admin_id = request.headers.get('X-User-Id')
    if not admin_id:
        return jsonify({
            'success': False,
            'error': 'Admin authentication required'
        }), 401
    
    auth_check = require_admin(int(admin_id))
    if auth_check:
        return jsonify({'success': False, 'error': auth_check['error']}), auth_check['status']
    
    status_filter = request.args.get('status', 'active')
    
    if status_filter == 'all':
        users = User.query.all()
    else:
        users = User.query.filter_by(status=status_filter).all()
    
    return jsonify({
        'success': True,
        'users': [user.to_dict() for user in users]
    }), 200


# Delete User (Soft Delete - Admin Only)
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    admin_id = request.headers.get('X-User-Id')
    if not admin_id:
        return jsonify({
            'success': False,
            'error': 'Admin authentication required'
        }), 401
    
    auth_check = require_admin(int(admin_id))
    if auth_check:
        return jsonify({'success': False, 'error': auth_check['error']}), auth_check['status']
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404
    
    if user.role == 'admin':
        return jsonify({
            'success': False,
            'error': 'Cannot delete admin users'
        }), 403
    
    # Soft delete
    user.status = 'deleted'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User deleted successfully'
    }), 200

    if not course:
        return jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404
    
    course.status = 'deleted'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Course deactivated successfully',
        'course': course.to_dict()
    }), 200


# =====================================================
# REVIEW MODERATION
# =====================================================

# Get All Reviews (Admin View)
@admin_bp.route('/reviews', methods=['GET'])
def get_all_reviews_admin():
    admin_id = request.headers.get('X-User-Id')
    if not admin_id:
        return jsonify({
            'success': False,
            'error': 'Admin authentication required'
        }), 401
    
    auth_check = require_admin(int(admin_id))
    if auth_check:
        return jsonify({'success': False, 'error': auth_check['error']}), auth_check['status']
    
    status_filter = request.args.get('status', 'active')
    
    if status_filter == 'all':
        reviews = Review.query.all()
    else:
        reviews = Review.query.filter_by(status=status_filter).all()
    
    return jsonify({
        'success': True,
        'reviews': [review.to_dict(include_user=True) for review in reviews]
    }), 200


# Remove Review (Soft Delete)
@admin_bp.route('/reviews/<int:review_id>/remove', methods=['PUT'])
def remove_review(review_id):
    admin_id = request.headers.get('X-User-Id')
    if not admin_id:
        return jsonify({
            'success': False,
            'error': 'Admin authentication required'
        }), 401
    
    auth_check = require_admin(int(admin_id))
    if auth_check:
        return jsonify({'success': False, 'error': auth_check['error']}), auth_check['status']
    
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
        'message': 'Review removed successfully'
    }), 200


# Restore Review
@admin_bp.route('/reviews/<int:review_id>/restore', methods=['PUT'])
def restore_review(review_id):
    admin_id = request.headers.get('X-User-Id')
    if not admin_id:
        return jsonify({
            'success': False,
            'error': 'Admin authentication required'
        }), 401
    
    auth_check = require_admin(int(admin_id))
    if auth_check:
        return jsonify({'success': False, 'error': auth_check['error']}), auth_check['status']
    
    review = Review.query.get(review_id)
    if not review:
        return jsonify({
            'success': False,
            'error': 'Review not found'
        }), 404
    
    review.status = 'active'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Review restored successfully'
    }), 200


# =====================================================
# RATING MODERATION
# =====================================================

# Get All Ratings (Admin View)
@admin_bp.route('/ratings', methods=['GET'])
def get_all_ratings_admin():
    admin_id = request.headers.get('X-User-Id')
    if not admin_id:
        return jsonify({
            'success': False,
            'error': 'Admin authentication required'
        }), 401
    
    auth_check = require_admin(int(admin_id))
    if auth_check:
        return jsonify({'success': False, 'error': auth_check['error']}), auth_check['status']
    
    status_filter = request.args.get('status', 'active')
    
    if status_filter == 'all':
        ratings = Rating.query.all()
    else:
        ratings = Rating.query.filter_by(status=status_filter).all()
    
    return jsonify({
        'success': True,
        'ratings': [rating.to_dict() for rating in ratings]
    }), 200


# Remove Rating (Soft Delete)
@admin_bp.route('/ratings/<int:rating_id>/remove', methods=['PUT'])
def remove_rating(rating_id):
    admin_id = request.headers.get('X-User-Id')
    if not admin_id:
        return jsonify({
            'success': False,
            'error': 'Admin authentication required'
        }), 401
    
    auth_check = require_admin(int(admin_id))
    if auth_check:
        return jsonify({'success': False, 'error': auth_check['error']}), auth_check['status']
    
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
        'message': 'Rating removed successfully'
    }), 200


# Restore Rating
@admin_bp.route('/ratings/<int:rating_id>/restore', methods=['PUT'])
def restore_rating(rating_id):
    admin_id = request.headers.get('X-User-Id')
    if not admin_id:
        return jsonify({
            'success': False,
            'error': 'Admin authentication required'
        }), 401
    
    auth_check = require_admin(int(admin_id))
    if auth_check:
        return jsonify({'success': False, 'error': auth_check['error']}), auth_check['status']
    
    rating = Rating.query.get(rating_id)
    if not rating:
        return jsonify({
            'success': False,
            'error': 'Rating not found'
        }), 404
    
    rating.status = 'active'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Rating restored successfully'
    }), 200


# =====================================================
# ANALYTICS & STATS
# =====================================================

# Get Platform Statistics
@admin_bp.route('/stats', methods=['GET'])
def get_platform_stats():
    admin_id = request.headers.get('X-User-Id')
    if not admin_id:
        return jsonify({
            'success': False,
            'error': 'Admin authentication required'
        }), 401
    
    auth_check = require_admin(int(admin_id))
    if auth_check:
        return jsonify({'success': False, 'error': auth_check['error']}), auth_check['status']
    
    stats = {
        'users': {
            'total': User.query.count(),
            'active': User.query.filter_by(status='active').count(),
            'learners': User.query.filter_by(role='learner', status='active').count(),
            'instructors': User.query.filter_by(role='instructor', status='active').count(),
            'admins': User.query.filter_by(role='admin', status='active').count()
        },
        'courses': {
            'total': Course.query.count(),
            'active': Course.query.filter_by(status='active').count(),
            'unpublished': Course.query.filter_by(status='unpublished').count(),
            'deleted': Course.query.filter_by(status='deleted').count()
        },
        'enrollments': {
            'total': Enrollment.query.count(),
            'active': Enrollment.query.filter_by(status='active').count(),
            'completed': Enrollment.query.filter_by(status='completed').count()
        },
        'content': {
            'reviews': Review.query.filter_by(status='active').count(),
            'ratings': Rating.query.filter_by(status='active').count()
        }
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    }), 200
