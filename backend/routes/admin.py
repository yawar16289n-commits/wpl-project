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


# User deletion is now handled by /users/<user_id> DELETE endpoint
# which supports both self-deletion and admin deletion