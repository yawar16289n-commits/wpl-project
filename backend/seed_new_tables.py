import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from database import db
from models import Profile, CourseDetail, CourseCategory, Progress
from datetime import datetime
import json

app = create_app()

def seed_new_tables():
    with app.app_context():
        # Clear existing data
        Progress.query.delete()
        CourseDetail.query.delete()
        Profile.query.delete()
        CourseCategory.query.delete()
        db.session.commit()
        
        # Seed Profiles (for 5 users: IDs 26-30)
        profiles = [
            Profile(
                user_id=26,  # student1@test.com
                bio="Lifelong learner passionate about artificial intelligence and data analytics.",
                profile_picture="https://picsum.photos/seed/user26/200",
                social_links=json.dumps({
                    "twitter": "https://twitter.com/student1"
                }),
                expertise=json.dumps(["Python", "Data Analysis"]),
                education=json.dumps([
                    {"degree": "BS in Computer Science", "institution": "University of Washington", "year": 2020}
                ])
            ),
            Profile(
                user_id=27,  # student2@test.com
                bio="Software engineer exploring machine learning and cloud technologies.",
                profile_picture="https://picsum.photos/seed/user27/200",
                expertise=json.dumps(["JavaScript", "Cloud", "APIs"]),
                education=json.dumps([
                    {"degree": "BS in Information Technology", "institution": "Georgia Tech", "year": 2021}
                ])
            ),
            Profile(
                user_id=28,  # yawar@iqra.com - Instructor
                bio="Passionate educator with 10+ years of experience in data science and machine learning.",
                profile_picture="https://picsum.photos/seed/user28/200",
                website="https://yawar-iqra.com",
                social_links=json.dumps({
                    "linkedin": "https://linkedin.com/in/yawar",
                    "twitter": "https://twitter.com/yawar",
                    "github": "https://github.com/yawar"
                }),
                expertise=json.dumps(["Data Science", "Machine Learning", "Python", "Statistics"]),
                education=json.dumps([
                    {"degree": "PhD in Computer Science", "institution": "MIT", "year": 2010},
                    {"degree": "MS in Data Science", "institution": "Stanford", "year": 2005}
                ])
            ),
            Profile(
                user_id=29,  # balti@yahoo.com - Instructor
                bio="Full-stack developer and tech instructor specializing in web development and cloud technologies.",
                profile_picture="https://picsum.photos/seed/user29/200",
                website="https://balti-dev.com",
                social_links=json.dumps({
                    "linkedin": "https://linkedin.com/in/balti",
                    "github": "https://github.com/balti"
                }),
                expertise=json.dumps(["Web Development", "Cloud Computing", "DevOps", "React"]),
                education=json.dumps([
                    {"degree": "MS in Software Engineering", "institution": "UC Berkeley", "year": 2015}
                ])
            ),
            Profile(
                user_id=30,  # meta@facebook.com
                bio="Data enthusiast learning to build intelligent systems.",
                profile_picture="https://picsum.photos/seed/user30/200",
                expertise=json.dumps(["Data Science", "Python"]),
                education=json.dumps([
                    {"degree": "BS in Statistics", "institution": "UCLA", "year": 2022}
                ])
            )
        ]
        db.session.add_all(profiles)
        db.session.commit()  # Commit profiles first
        
        # Seed Course Categories (parent categories first)
        parent_categories = [
            CourseCategory(
                name="Data Science",
                slug="data-science",
                description="Learn data analysis, machine learning, and statistical modeling",
                icon="📊"
            ),
            CourseCategory(
                name="Programming",
                slug="programming",
                description="Master programming languages and software development",
                icon="💻"
            ),
            CourseCategory(
                name="Cloud Computing",
                slug="cloud-computing",
                description="Deploy and scale applications in the cloud",
                icon="☁️"
            ),
            CourseCategory(
                name="Business",
                slug="business",
                description="Business analytics and strategy",
                icon="📈"
            )
        ]
        db.session.add_all(parent_categories)
        db.session.flush()  # Get parent IDs
        
        # Now add child categories
        child_categories = [
            CourseCategory(
                name="Machine Learning",
                slug="machine-learning",
                description="Build intelligent systems with ML and AI",
                icon="🤖",
                parent_id=parent_categories[0].id  # Data Science
            ),
            CourseCategory(
                name="Web Development",
                slug="web-development",
                description="Create modern web applications",
                icon="🌐",
                parent_id=parent_categories[1].id  # Programming
            )
        ]
        db.session.add_all(child_categories)
        db.session.flush()
        
        # Seed Course Details (for 4 courses: IDs 13, 14, 15, 16)
        course_details = [
            CourseDetail(
                course_id=13,  # Complete Data Science Bootcamp
                requirements=json.dumps([
                    "Basic understanding of programming concepts",
                    "Familiarity with Python syntax (helpful but not required)",
                    "Computer with Python 3.8+ installed",
                    "Enthusiasm to learn!"
                ]),
                who_is_for=json.dumps([
                    "Beginners who want to start with data science",
                    "Developers looking to add data skills",
                    "Students preparing for data science careers",
                    "Business analysts wanting to learn Python"
                ]),
                objectives=json.dumps([
                    "Master Python fundamentals and data structures",
                    "Perform data analysis with Pandas and NumPy",
                    "Create visualizations with Matplotlib and Seaborn",
                    "Build and evaluate machine learning models",
                    "Work with real-world datasets"
                ]),
                syllabus=json.dumps([
                    {
                        "module": "Module 1: Python Basics",
                        "topics": ["Variables & Data Types", "Control Flow", "Functions", "OOP Basics"]
                    },
                    {
                        "module": "Module 2: Data Analysis",
                        "topics": ["NumPy Arrays", "Pandas DataFrames", "Data Cleaning", "Exploratory Analysis"]
                    },
                    {
                        "module": "Module 3: Visualization",
                        "topics": ["Matplotlib", "Seaborn", "Interactive Plots", "Dashboards"]
                    },
                    {
                        "module": "Module 4: Machine Learning",
                        "topics": ["Scikit-learn", "Supervised Learning", "Model Evaluation", "Real Projects"]
                    }
                ]),
                faq=json.dumps([
                    {
                        "question": "Do I need prior programming experience?",
                        "answer": "No! This course starts from the basics and builds up progressively."
                    },
                    {
                        "question": "How long will it take to complete?",
                        "answer": "Most students complete the course in 6-8 weeks with 5-7 hours per week."
                    },
                    {
                        "question": "Will I get a certificate?",
                        "answer": "Yes, you'll receive a certificate of completion after finishing all modules."
                    }
                ])
            ),
            CourseDetail(
                course_id=14,  # Advanced Machine Learning
                requirements=json.dumps([
                    "Strong Python programming skills",
                    "Understanding of linear algebra and calculus",
                    "Basic probability and statistics",
                    "Familiarity with Jupyter notebooks"
                ]),
                who_is_for=json.dumps([
                    "Data scientists wanting to specialize in ML",
                    "Software engineers transitioning to AI",
                    "Graduate students in related fields",
                    "Researchers in quantitative domains"
                ]),
                objectives=json.dumps([
                    "Understand ML algorithms from scratch",
                    "Implement neural networks and deep learning",
                    "Master feature engineering and model tuning",
                    "Deploy ML models to production",
                    "Work on industry-level projects"
                ]),
                syllabus=json.dumps([
                    {
                        "module": "Advanced Algorithms",
                        "topics": ["Ensemble Methods", "Deep Learning", "NLP", "Computer Vision"]
                    },
                    {
                        "module": "Model Deployment",
                        "topics": ["APIs", "Containerization", "Cloud Platforms", "Monitoring"]
                    }
                ]),
                faq=json.dumps([
                    {
                        "question": "Is this suitable for beginners?",
                        "answer": "No, this is an advanced course. You should have ML fundamentals first."
                    }
                ])
            ),
            CourseDetail(
                course_id=15,  # React Complete Guide 2024 (Web Development)
                requirements=json.dumps([
                    "Basic understanding of AWS services",
                    "Familiarity with cloud concepts",
                    "General IT knowledge"
                ]),
                who_is_for=json.dumps([
                    "IT professionals seeking AWS certification",
                    "System administrators moving to cloud",
                    "Developers working with AWS",
                    "Students preparing for cloud careers"
                ]),
                objectives=json.dumps([
                    "Master core AWS services (EC2, S3, RDS, Lambda)",
                    "Design scalable cloud architectures",
                    "Pass AWS Solutions Architect exam",
                    "Implement security best practices",
                    "Optimize costs and performance"
                ]),
                syllabus=json.dumps([
                    {
                        "module": "AWS Fundamentals",
                        "topics": ["IAM", "VPC", "EC2", "S3"]
                    },
                    {
                        "module": "Advanced Services",
                        "topics": ["Lambda", "DynamoDB", "CloudFormation", "ECS/EKS"]
                    }
                ]),
                faq=json.dumps([
                    {
                        "question": "Will this prepare me for certification?",
                        "answer": "Yes, this course covers all topics for AWS Solutions Architect Associate."
                    }
                ])
            ),
            CourseDetail(
                course_id=16,  # Python for Beginners
                requirements=json.dumps([
                    "HTML, CSS, JavaScript fundamentals",
                    "Understanding of React basics",
                    "Node.js knowledge helpful"
                ]),
                who_is_for=json.dumps([
                    "Frontend developers learning full-stack",
                    "Backend developers adding frontend skills",
                    "Students building modern web apps"
                ]),
                objectives=json.dumps([
                    "Build full-stack apps with Next.js",
                    "Master server-side rendering",
                    "Implement authentication and APIs",
                    "Deploy to production",
                    "Optimize performance"
                ]),
                syllabus=json.dumps([
                    {
                        "module": "Next.js Fundamentals",
                        "topics": ["App Router", "SSR/SSG", "API Routes", "Authentication"]
                    },
                    {
                        "module": "Advanced Topics",
                        "topics": ["Performance", "SEO", "Deployment", "Real Projects"]
                    }
                ]),
                faq=json.dumps([
                    {
                        "question": "Do I need React experience?",
                        "answer": "Yes, you should be comfortable with React basics before starting."
                    }
                ])
            )
        ]
        db.session.add_all(course_details)
        
        # Seed Progress (for enrolled students)
        # User 26 (student1) in courses 13,14 and User 27 (student2) in courses 13,15
        progress_records = [
            Progress(
                user_id=26,  # student1
                course_id=13,  # Data Science Bootcamp
                lecture_id=34,  # Python Basics (first lecture of course 13)
                completed_lectures=json.dumps([34]),
                current_lecture=35,
                time_spent=125,  # minutes
                notes=json.dumps([
                    {"lecture_id": 34, "note": "Great introduction to Python basics!"}
                ])
            ),
            Progress(
                user_id=26,  # student1
                course_id=14,  # Advanced ML
                lecture_id=37,  # Neural Networks (first lecture of course 14)
                completed_lectures=json.dumps([37, 38]),
                current_lecture=39,
                time_spent=280,
                notes=json.dumps([
                    {"lecture_id": 37, "note": "ML algorithms are fascinating"},
                    {"lecture_id": 38, "note": "Need to practice neural networks more"}
                ])
            ),
            Progress(
                user_id=27,  # student2
                course_id=13,  # Data Science Bootcamp
                lecture_id=34,  # Python Basics
                completed_lectures=json.dumps([]),
                current_lecture=34,
                time_spent=45,
                notes=json.dumps([])
            ),
            Progress(
                user_id=27,  # student2
                course_id=15,  # React Guide
                lecture_id=40,  # React Fundamentals (first lecture of course 15)
                completed_lectures=json.dumps([40]),
                current_lecture=41,
                time_spent=95,
                notes=json.dumps([
                    {"lecture_id": 40, "note": "React hooks are powerful!"}
                ])
            )
        ]
        db.session.add_all(progress_records)
        
        db.session.commit()
        
        print("✅ Seed data added successfully!")
        print("\n📊 Summary:")
        print(f"  - Profiles: {Profile.query.count()} records")
        print(f"  - Course Categories: {CourseCategory.query.count()} records")
        print(f"  - Course Details: {CourseDetail.query.count()} records")
        print(f"  - Progress: {Progress.query.count()} records")

if __name__ == '__main__':
    seed_new_tables()
