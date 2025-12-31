"""
Script to create an admin user
"""
from app import create_app
from models import User, Profile
from database import db
from datetime import datetime

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@admin.com', role='admin').first()
        
        if admin:
            print(f"Admin user already exists: {admin.email}")
            return
        
        # Create admin user
        admin = User(
            name='Admin',
            email='admin@admin.com',
            password='admin',
            role='admin',
            status='active',
            created_at=datetime.utcnow()
        )
        
        db.session.add(admin)
        db.session.commit()
        
        # Create profile for admin
        profile = Profile(
            user_id=admin.id,
            bio='System Administrator',
            status='active'
        )
        
        db.session.add(profile)
        db.session.commit()
        
        print("Admin user created successfully!")
        print(f"Email: admin@admin.com")
        print(f"Password: admin")
        print(f"User ID: {admin.id}")

if __name__ == '__main__':
    create_admin()
