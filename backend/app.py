import os
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from database import db
from routes import api_bp

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    # Disable automatic trailing slash redirects
    app.url_map.strict_slashes = False

    # Configure CORS with credentials support
    CORS(app, 
         origins=["http://localhost:3000"],
         allow_headers=["Content-Type", "X-User-Id"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True,
         expose_headers=["Content-Type", "X-User-Id"])


    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(api_bp)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'message': 'Server is running'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '127.0.0.1')
    app.run(debug=True, host=host, port=port)
