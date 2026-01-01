from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from routes.users import users_bp
from routes.profiles import profiles_bp
from routes.courses import courses_bp
from routes.enrollments import enrollments_bp
from routes.lectures import lectures_bp
from routes.lecture_resources import lecture_resources_bp
from routes.reviews import reviews_bp
from routes.ratings import ratings_bp
from routes.progress import progress_bp
from routes.dashboard import dashboard_bp

api_bp.register_blueprint(users_bp)
api_bp.register_blueprint(profiles_bp)
api_bp.register_blueprint(courses_bp)
api_bp.register_blueprint(enrollments_bp)
api_bp.register_blueprint(lectures_bp)
api_bp.register_blueprint(lecture_resources_bp)
api_bp.register_blueprint(reviews_bp)
api_bp.register_blueprint(ratings_bp)
api_bp.register_blueprint(progress_bp)
api_bp.register_blueprint(dashboard_bp)
