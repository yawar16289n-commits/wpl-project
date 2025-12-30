"""
Seed database with sample courses, users, and modules
"""
from app import create_app
from database import db
from models import User, Course, CourseModule
from datetime import datetime
import json

app = create_app()

def seed_database():
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        from models import Enrollment
        Enrollment.query.delete()
        CourseModule.query.delete()
        Course.query.delete()
        User.query.filter(User.role == 'instructor').delete()
        db.session.commit()
        
        from werkzeug.security import generate_password_hash
        
        # Create instructors
        print("Creating instructors...")
        instructors = [
            User(
                name='yawar',
                email='yawar@iqra.com',
                password=generate_password_hash('password123'),
                role='instructor',
                bio='yawar is a professor of data science with 15+ years of industry experience. He has led data science teams at Fortune 500 companies.',
                profile_picture='/placeholder.svg',
                created_at=datetime.utcnow()
            ),
            User(
                name='Meta Developers',
                email='meta@facebook.com',
                password=generate_password_hash('password123'),
                role='instructor',
                bio='The Meta Developers program is led by experienced engineers from Meta who have built production-grade React applications serving billions of users.',
                profile_picture='/placeholder.svg',
                created_at=datetime.utcnow()
            ),
            User(
                name='balti',
                email='balti@yahoo.com',
                password=generate_password_hash('password123'),
                role='instructor',
                bio='balti is the Co-founder of Coursera and an Adjunct Professor of Computer Science at Stanford University. He has published over 100 research papers in machine learning.',
                profile_picture='/placeholder.svg',
                created_at=datetime.utcnow()
            )
        ]
        
        for instructor in instructors:
            db.session.add(instructor)
        db.session.commit()
        
        # Create courses
        print("Creating courses...")
        courses_data = [
            {
                'title': 'Data Science Fundamentals',
                'description': 'Learn data science fundamentals including statistical analysis, data visualization, and predictive modeling.',
                'about': 'Master the core skills of data science. This comprehensive specialization covers data collection, cleaning, analysis, and visualization. You\'ll learn to work with real datasets and build predictive models using Python.',
                'instructor_id': instructors[0].id,
                'company': 'University of Colorado Boulder',
                'category': 'Data Science',
                'level': 'Beginner',
                'price': 49.00,
                'original_price': 99.00,
                'duration': '4-5 months',
                'image': '/placeholder.svg',
                'rating': 4.7,
                'total_students': 185000,
                'total_reviews': 3245,
                'is_published': True,
                'language': 'English',
                'subtitles': json.dumps(['English', 'Spanish', 'French', 'Chinese']),
                'skills': json.dumps(['Data Analysis', 'Python', 'Statistics', 'Visualization']),
                'learning_outcomes': json.dumps([
                    'Master data cleaning and preprocessing techniques',
                    'Perform statistical analysis and hypothesis testing',
                    'Create compelling data visualizations',
                    'Build predictive models using machine learning',
                    'Work with real-world datasets',
                    'Communicate data insights effectively'
                ]),
                'created_at': datetime.utcnow(),
                'modules': [
                    {'number': 1, 'title': 'Data Fundamentals', 'lessons': 24, 'duration': '10 hours'},
                    {'number': 2, 'title': 'Statistical Analysis & Probability', 'lessons': 28, 'duration': '12 hours'},
                    {'number': 3, 'title': 'Data Visualization & Communication', 'lessons': 22, 'duration': '9 hours'},
                    {'number': 4, 'title': 'Predictive Modeling', 'lessons': 30, 'duration': '14 hours'}
                ]
            },
            {
                'title': 'Web Development with React',
                'description': 'Build modern web applications with React. Learn component-based architecture, state management, and advanced patterns.',
                'about': 'Learn to build scalable web applications with React from Meta engineers. This course covers modern JavaScript, React fundamentals, state management with Redux, and testing practices.',
                'instructor_id': instructors[1].id,
                'company': 'Meta',
                'category': 'Web Development',
                'level': 'Intermediate',
                'price': 49.00,
                'original_price': 99.00,
                'duration': '3-4 months',
                'image': '/placeholder.svg',
                'rating': 4.8,
                'total_students': 225000,
                'total_reviews': 4156,
                'is_published': True,
                'language': 'English',
                'subtitles': json.dumps(['English', 'Spanish', 'German', 'Japanese']),
                'skills': json.dumps(['React', 'JavaScript', 'Web Development', 'CSS']),
                'learning_outcomes': json.dumps([
                    'Master modern JavaScript ES6+ syntax',
                    'Build reusable React components',
                    'Manage application state effectively',
                    'Integrate with REST and GraphQL APIs',
                    'Implement authentication and authorization',
                    'Deploy React applications to production'
                ]),
                'created_at': datetime.utcnow(),
                'modules': [
                    {'number': 1, 'title': 'JavaScript Fundamentals', 'lessons': 32, 'duration': '14 hours'},
                    {'number': 2, 'title': 'React Basics & Components', 'lessons': 36, 'duration': '16 hours'},
                    {'number': 3, 'title': 'State Management & APIs', 'lessons': 28, 'duration': '12 hours'},
                    {'number': 4, 'title': 'Advanced React Patterns', 'lessons': 24, 'duration': '11 hours'}
                ]
            },
            {
                'title': 'Machine Learning Specialization',
                'description': 'Learn Machine Learning from the best in the field. This specialization covers the fundamentals of machine learning and deep learning.',
                'about': 'Master Machine Learning fundamentals and build your career in AI. Learn supervised learning, unsupervised learning, and reinforcement learning. This comprehensive specialization will equip you with the skills to understand and apply machine learning techniques to real-world problems.',
                'instructor_id': instructors[2].id,
                'company': 'DeepLearning.AI',
                'category': 'Machine Learning',
                'level': 'Beginner',
                'price': 49.00,
                'original_price': 99.00,
                'duration': '3-4 months',
                'image': '/placeholder.svg',
                'rating': 4.9,
                'total_students': 350000,
                'total_reviews': 5234,
                'is_published': True,
                'language': 'English',
                'subtitles': json.dumps(['English', 'Spanish', 'French', 'Mandarin']),
                'skills': json.dumps(['Machine Learning', 'Python', 'Neural Networks', 'Deep Learning']),
                'learning_outcomes': json.dumps([
                    'Understand the core concepts of machine learning and how to apply them',
                    'Build and train neural networks using TensorFlow',
                    'Implement supervised and unsupervised learning algorithms',
                    'Apply machine learning to real-world problems and datasets',
                    'Develop practical machine learning projects',
                    'Master Python programming for machine learning'
                ]),
                'created_at': datetime.utcnow(),
                'modules': [
                    {'number': 1, 'title': 'Supervised Machine Learning: Regression and Classification', 'lessons': 27, 'duration': '12 hours'},
                    {'number': 2, 'title': 'Advanced Learning Algorithms', 'lessons': 34, 'duration': '15 hours'},
                    {'number': 3, 'title': 'Unsupervised Learning, Recommenders, Reinforcement Learning', 'lessons': 31, 'duration': '14 hours'}
                ]
            }
        ]
        
        for course_data in courses_data:
            modules_data = course_data.pop('modules')
            course = Course(**course_data)
            db.session.add(course)
            db.session.flush()  # Get course ID
            
            # Add modules
            for module_data in modules_data:
                module = CourseModule(course_id=course.id, **module_data)
                db.session.add(module)
        
        db.session.commit()
        print("✅ Database seeded successfully!")
        print(f"Created {len(instructors)} instructors and {len(courses_data)} courses")

if __name__ == '__main__':
    seed_database()
