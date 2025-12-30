from app import create_app
from database import db
from models import User, Course, CourseModule, Enrollment, Review, Rating
from datetime import datetime
from werkzeug.security import generate_password_hash

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("Clearing existing data...")
        Review.query.delete()
        Rating.query.delete()
        Enrollment.query.delete()
        CourseModule.query.delete()
        Course.query.delete()
        User.query.delete()
        db.session.commit()
        
        print("Creating users...")
        # Create students
        student1 = User(
            name='John Student',
            email='student1@test.com',
            password=generate_password_hash('password123'),
            role='learner',
            bio='Passionate learner eager to expand my skills.',
            profile_picture='/placeholder.svg',
            created_at=datetime.utcnow()
        )
        
        student2 = User(
            name='Sarah Learner',
            email='student2@test.com',
            password=generate_password_hash('password123'),
            role='learner',
            bio='Always curious about new technologies.',
            profile_picture='/placeholder.svg',
            created_at=datetime.utcnow()
        )
        
        # Create instructors
        instructor1 = User(
            name='yawar',
            email='yawar@iqra.com',
            password=generate_password_hash('password123'),
            role='instructor',
            bio='yawar is a professor of data science with 15+ years of industry experience.',
            profile_picture='/placeholder.svg',
            created_at=datetime.utcnow()
        )
        
        instructor2 = User(
            name='balti',
            email='balti@yahoo.com',
            password=generate_password_hash('password123'),
            role='instructor',
            bio='balti is the Co-founder of Coursera and expert in machine learning.',
            profile_picture='/placeholder.svg',
            created_at=datetime.utcnow()
        )
        
        instructor3 = User(
            name='Meta Developers',
            email='meta@facebook.com',
            password=generate_password_hash('password123'),
            role='instructor',
            bio='Leading React developers from Meta.',
            profile_picture='/placeholder.svg',
            created_at=datetime.utcnow()
        )
        
        db.session.add_all([student1, student2, instructor1, instructor2, instructor3])
        db.session.commit()
        
        print("Creating courses...")
        # Course 1 - Data Science
        course1 = Course(
            title='Complete Data Science Bootcamp',
            description='Master data science from basics to advanced topics including Python, statistics, and machine learning.',
            about='This comprehensive course covers everything you need to become a data scientist.',
            instructor_id=instructor1.id,
            company='Iqra University',
            category='Data Science',
            level='Beginner',
            duration='40 hours',
            image='https://picsum.photos/400/225?random=1',
            rating=4.5,
            total_students=1250,
            total_reviews=234,
            is_published=True,
            language='English',
            subtitles='["English", "Arabic"]',
            skills='["Python", "Pandas", "NumPy", "Machine Learning"]',
            learning_outcomes='["Master Python for data analysis", "Build ML models", "Visualize data effectively"]',
            created_at=datetime.utcnow()
        )
        
        # Course 2 - Machine Learning
        course2 = Course(
            title='Advanced Machine Learning',
            description='Deep dive into machine learning algorithms, neural networks, and practical applications.',
            about='Learn advanced ML techniques used in industry.',
            instructor_id=instructor2.id,
            company='Stanford',
            category='Machine Learning',
            level='Advanced',
            duration='60 hours',
            image='https://picsum.photos/400/225?random=2',
            rating=4.8,
            total_students=890,
            total_reviews=156,
            is_published=True,
            language='English',
            subtitles='["English"]',
            skills='["TensorFlow", "PyTorch", "Deep Learning", "Neural Networks"]',
            learning_outcomes='["Build neural networks", "Implement CNNs and RNNs", "Deploy ML models"]',
            created_at=datetime.utcnow()
        )
        
        # Course 3 - React
        course3 = Course(
            title='React Complete Guide 2024',
            description='Build modern web applications with React, from fundamentals to advanced patterns.',
            about='Master React and become a professional frontend developer.',
            instructor_id=instructor3.id,
            company='Meta',
            category='Web Development',
            level='Intermediate',
            duration='35 hours',
            image='https://picsum.photos/400/225?random=3',
            rating=4.7,
            total_students=2100,
            total_reviews=412,
            is_published=True,
            language='English',
            subtitles='["English", "Spanish"]',
            skills='["React", "JavaScript", "Hooks", "Redux"]',
            learning_outcomes='["Build React apps", "Master Hooks", "State management with Redux"]',
            created_at=datetime.utcnow()
        )
        
        # Course 4 - Python Programming
        course4 = Course(
            title='Python for Beginners',
            description='Learn Python programming from scratch with hands-on projects.',
            about='Perfect for absolute beginners who want to learn programming.',
            instructor_id=instructor1.id,
            company='Iqra University',
            category='Programming',
            level='Beginner',
            duration='25 hours',
            image='https://picsum.photos/400/225?random=4',
            rating=4.6,
            total_students=3200,
            total_reviews=521,
            is_published=True,
            language='English',
            skills='["Python", "OOP", "Problem Solving"]',
            learning_outcomes='["Write Python programs", "Understand OOP", "Build projects"]',
            created_at=datetime.utcnow()
        )
        
        db.session.add_all([course1, course2, course3, course4])
        db.session.commit()
        
        print("Creating course modules...")
        # Modules for Course 1
        modules1 = [
            CourseModule(course_id=course1.id, number=1, title='Python Basics', lessons=12, duration='4 hours'),
            CourseModule(course_id=course1.id, number=2, title='Data Analysis with Pandas', lessons=15, duration='5 hours'),
            CourseModule(course_id=course1.id, number=3, title='Machine Learning Fundamentals', lessons=18, duration='6 hours'),
        ]
        
        # Modules for Course 2
        modules2 = [
            CourseModule(course_id=course2.id, number=1, title='Neural Networks', lessons=10, duration='4 hours'),
            CourseModule(course_id=course2.id, number=2, title='Deep Learning', lessons=12, duration='5 hours'),
            CourseModule(course_id=course2.id, number=3, title='Advanced Topics', lessons=14, duration='6 hours'),
        ]
        
        # Modules for Course 3
        modules3 = [
            CourseModule(course_id=course3.id, number=1, title='React Fundamentals', lessons=10, duration='3 hours'),
            CourseModule(course_id=course3.id, number=2, title='Hooks and State', lessons=12, duration='4 hours'),
            CourseModule(course_id=course3.id, number=3, title='Advanced Patterns', lessons=14, duration='5 hours'),
        ]
        
        db.session.add_all(modules1 + modules2 + modules3)
        db.session.commit()
        
        print("Creating enrollments...")
        # Student1 enrollments
        enrollment1 = Enrollment(
            user_id=student1.id,
            course_id=course1.id,
            progress=45,
            status='active',
            enrolled_at=datetime.utcnow()
        )
        
        enrollment2 = Enrollment(
            user_id=student1.id,
            course_id=course3.id,
            progress=100,
            status='completed',
            enrolled_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        # Student2 enrollments
        enrollment3 = Enrollment(
            user_id=student2.id,
            course_id=course2.id,
            progress=25,
            status='active',
            enrolled_at=datetime.utcnow()
        )
        
        db.session.add_all([enrollment1, enrollment2, enrollment3])
        db.session.commit()
        
        print("Creating reviews and ratings...")
        # Reviews
        review1 = Review(
            course_id=course1.id,
            user_id=student1.id,
            comment='Great course! Very comprehensive and well-structured.',
            created_at=datetime.utcnow()
        )
        
        review2 = Review(
            course_id=course3.id,
            user_id=student1.id,
            comment='Excellent React course. Learned so much!',
            created_at=datetime.utcnow()
        )
        
        review3 = Review(
            course_id=course2.id,
            user_id=student2.id,
            comment='Advanced content is challenging but rewarding.',
            created_at=datetime.utcnow()
        )
        
        # Ratings
        rating1 = Rating(course_id=course1.id, user_id=student1.id, rating=5, created_at=datetime.utcnow())
        rating2 = Rating(course_id=course3.id, user_id=student1.id, rating=5, created_at=datetime.utcnow())
        rating3 = Rating(course_id=course2.id, user_id=student2.id, rating=4, created_at=datetime.utcnow())
        
        db.session.add_all([review1, review2, review3, rating1, rating2, rating3])
        db.session.commit()
        
        print("✅ Database seeded successfully!")
        print("\nTest Accounts:")
        print("Students:")
        print("  - student1@test.com / password123")
        print("  - student2@test.com / password123")
        print("Instructors:")
        print("  - yawar@iqra.com / password123")
        print("  - balti@yahoo.com / password123")
        print("  - meta@facebook.com / password123")

if __name__ == '__main__':
    seed_database()
