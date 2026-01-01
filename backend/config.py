import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Parse CORS origins
    frontend_urls = os.getenv('FRONTEND_URL', 'http://localhost:3000,http://localhost:3001')
    CORS_ORIGINS = [url.strip() for url in frontend_urls.split(',')]
    
    # Ensure all localhost variants are included for development
    if DEBUG:
        CORS_ORIGINS.extend([
            'http://localhost:3000',
            'http://localhost:3001',
            'http://127.0.0.1:3000',
            'http://127.0.0.1:3001'
        ])
        CORS_ORIGINS = list(set(CORS_ORIGINS))  # Remove duplicates
