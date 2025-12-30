from datetime import datetime
from app import db
from sqlalchemy import Numeric
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('learner', 'instructor', 'admin'), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    about = db.Column(db.Text, nullable=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Enum('Beginner', 'Intermediate', 'Advanced'), default='Beginner')
    duration = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    rating = db.Column(Numeric(3, 2), default=0.00)
    total_students = db.Column(db.Integer, default=0)
    total_reviews = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(50), default='English')
    subtitles = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    learning_outcomes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime)
    
    def to_dict(self, include_instructor=False, include_modules=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'about': self.about,
            'instructor_id': self.instructor_id,
            'company': self.company,
            'category': self.category,
            'level': self.level,
            'duration': self.duration,
            'image': self.image,
            'rating': float(self.rating) if self.rating else 0.0,
            'total_students': self.total_students,
            'students': self.total_students,
            'total_reviews': self.total_reviews,
            'reviews': self.total_reviews,
            'language': self.language,
            'subtitles': json.loads(self.subtitles) if self.subtitles else [],
            'skills': json.loads(self.skills) if self.skills else [],
            'learning_outcomes': json.loads(self.learning_outcomes) if self.learning_outcomes else [],
            'learningOutcomes': json.loads(self.learning_outcomes) if self.learning_outcomes else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_instructor:
            instructor = User.query.get(self.instructor_id)
            if instructor:
                data['instructor'] = instructor.name
                data['instructor_bio'] = instructor.bio
                data['instructor_image'] = instructor.profile_picture
        
        if include_modules:
            modules = CourseModule.query.filter_by(course_id=self.id).order_by(CourseModule.number).all()
            data['courses'] = [module.to_dict() for module in modules]
        
        return data


class CourseModule(db.Model):
    __tablename__ = 'course_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    lessons = db.Column(db.Integer, default=0)
    duration = db.Column(db.String(50), nullable=True)
    
    @property
    def resource_count(self):
        """Get the number of resources for this lecture"""
        from models import LectureResource
        return LectureResource.query.filter_by(lecture_id=self.id).count()
    
    def to_dict(self):
        # Auto-calculate lessons based on resource count
        actual_lessons = self.resource_count
        
        return {
            'id': self.id,
            'course_id': self.course_id,
            'number': self.number,
            'title': self.title,
            'lessons': actual_lessons,  # Return calculated count
            'duration': self.duration
        }


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('active', 'completed', 'dropped'), default='active')
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),)
    
    def to_dict(self, include_course=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'progress': self.progress,
            'status': self.status,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
        
        if include_course:
            course = Course.query.get(self.course_id)
            if course:
                data['course'] = course.to_dict(include_instructor=True)
        
        return data


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_user=False):
        data = {
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user:
            user = User.query.get(self.user_id)
            if user:
                data['user_name'] = user.name
                data['user_image'] = user.profile_picture
        
        return data


class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course_rating'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class LectureResource(db.Model):
    __tablename__ = 'lecture_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('course_modules.id'), nullable=False)
    resource_type = db.Column(db.Enum('video', 'pdf', 'link', 'document', 'quiz'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'lecture_id': self.lecture_id,
            'resource_type': self.resource_type,
            'title': self.title,
            'url': self.url,
            'content': self.content,
            'duration': self.duration,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    social_links = db.Column(db.Text, nullable=True)
    expertise = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bio': self.bio,
            'profile_picture': self.profile_picture,
            'website': self.website,
            'social_links': json.loads(self.social_links) if self.social_links else [],
            'expertise': json.loads(self.expertise) if self.expertise else [],
            'education': json.loads(self.education) if self.education else [],
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CourseDetail(db.Model):
    __tablename__ = 'course_details'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, unique=True)
    requirements = db.Column(db.Text, nullable=True)
    who_is_for = db.Column(db.Text, nullable=True)
    objectives = db.Column(db.Text, nullable=True)
    syllabus = db.Column(db.Text, nullable=True)
    faq = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'requirements': json.loads(self.requirements) if self.requirements else [],
            'who_is_for': json.loads(self.who_is_for) if self.who_is_for else [],
            'objectives': json.loads(self.objectives) if self.objectives else [],
            'syllabus': self.syllabus,
            'faq': json.loads(self.faq) if self.faq else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CourseCategory(db.Model):
    __tablename__ = 'course_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(255), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('course_categories.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'parent_id': self.parent_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Progress(db.Model):
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey('course_modules.id'), nullable=True)
    completed_lectures = db.Column(db.Text, nullable=True)
    current_lecture = db.Column(db.Integer, nullable=True)
    time_spent = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', 'lecture_id', name='unique_user_course_lecture_progress'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'lecture_id': self.lecture_id,
            'completed_lectures': json.loads(self.completed_lectures) if self.completed_lectures else [],
            'current_lecture': self.current_lecture,
            'time_spent': self.time_spent,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'notes': self.notes
        }
