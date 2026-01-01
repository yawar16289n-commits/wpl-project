from datetime import datetime
from database import db
from sqlalchemy import Numeric, func
import json


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('learner', 'instructor', 'admin'), nullable=False)
    status = db.Column(db.Enum('active', 'deleted'), default='active', nullable=False)
    created_at = db.Column(db.DateTime)
    
    def to_dict(self, include_profile=False):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_profile:
            profile = Profile.query.filter_by(user_id=self.id, status='active').first()
            if profile:
                data['profile_picture'] = profile.profile_picture
                data['bio'] = profile.bio
                data['website'] = profile.website
                data['social_links'] = json.loads(profile.social_links) if profile.social_links else []
                data['expertise'] = json.loads(profile.expertise) if profile.expertise else []
                data['education'] = json.loads(profile.education) if profile.education else []
        
        return data


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
    status = db.Column(db.Enum('active', 'unpublished', 'deleted'), default='unpublished', nullable=False)
    created_at = db.Column(db.DateTime)
    
    @property
    def rating(self):
        """Dynamically calculate average rating from Rating table"""
        avg = db.session.query(func.avg(Rating.rating)).filter(
            Rating.course_id == self.id,
            Rating.status == 'active'
        ).scalar()
        return round(float(avg), 1) if avg else 0.0
    
    @property
    def total_students(self):
        """Dynamically calculate total students from Enrollment table"""
        return Enrollment.query.filter(
            Enrollment.course_id == self.id,
            Enrollment.status.in_(['active', 'completed'])
        ).count()
    
    @property
    def total_reviews(self):
        """Dynamically calculate total reviews from Review table"""
        return Review.query.filter(
            Review.course_id == self.id,
            Review.status == 'active'
        ).count()
    
    def to_dict(self, include_instructor=False, include_modules=False, include_details=False, include_stats=False):
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
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Include stats by default for backwards compatibility
        if include_stats or True:
            data['rating'] = self.rating
            data['total_students'] = self.total_students
            data['total_reviews'] = self.total_reviews
        
        
        if include_instructor:
            instructor = User.query.get(self.instructor_id)
            if instructor:
                data['instructor'] = instructor.name
                # Fetch instructor profile data
                profile = Profile.query.filter_by(user_id=instructor.id, status='active').first()
                if profile:
                    data['instructor_bio'] = profile.bio
                    data['instructor_image'] = profile.profile_picture
                else:
                    data['instructor_bio'] = None
                    data['instructor_image'] = None
        
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
    status = db.Column(db.Enum('active', 'deleted'), default='active', nullable=False)
    
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
            'duration': self.duration,
            'status': self.status
        }


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    status = db.Column(db.Enum('active', 'completed', 'dropped', 'deleted'), default='active')
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),)
    
    @property
    def progress(self):
        """Dynamically calculate progress from Progress table"""
        # Import here to avoid circular import
        from models import Progress
        return Progress.calculate_course_progress(self.id)
    
    def to_dict(self, include_course=False, include_next_lecture=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'progress': self.progress,  # Dynamically calculated
            'status': self.status,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
        
        if include_course:
            course = Course.query.get(self.course_id)
            if course:
                data['course'] = course.to_dict(include_instructor=True)
        
        if include_next_lecture:
            from models import Progress
            next_lecture = Progress.get_next_lecture(self.id)
            if next_lecture:
                data['next_lecture'] = next_lecture.to_dict()
            else:
                data['next_lecture'] = None
        
        return data


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('active', 'deleted'), default='active', nullable=False)
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
                # Fetch user profile picture
                profile = Profile.query.filter_by(user_id=user.id, status='active').first()
                data['user_image'] = profile.profile_picture if profile else None
        
        return data


class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('active', 'deleted'), default='active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course_rating'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class LectureResource(db.Model):
    __tablename__ = 'lecture_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('course_modules.id'), nullable=False)
    resource_type = db.Column(db.Enum('video', 'pdf', 'link', 'document', 'quiz', 'text'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    order = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('active', 'deleted'), default='active', nullable=False)
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
    status = db.Column(db.Enum('active', 'deleted'), default='active', nullable=False)
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


class Progress(db.Model):
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), nullable=False)
    lecture_resource_id = db.Column(db.Integer, db.ForeignKey('lecture_resources.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('active', 'deleted'), default='active', nullable=False)
    
    __table_args__ = (db.UniqueConstraint('enrollment_id', 'lecture_resource_id', name='unique_enrollment_lecture'),)

    def to_dict(self):
        return {
            'id': self.id,
            'enrollment_id': self.enrollment_id,
            'lecture_resource_id': self.lecture_resource_id,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status
        }

    @staticmethod
    def calculate_course_progress(enrollment_id):
        """Calculate progress percentage for a course enrollment ignoring deleted lectures and progress"""
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment or enrollment.status == 'deleted':
            return 0

        # Get all active lecture resources for the course
        total_lectures = db.session.query(LectureResource).join(
            CourseModule, LectureResource.lecture_id == CourseModule.id
        ).filter(
            CourseModule.course_id == enrollment.course_id,
            LectureResource.status == 'active',
            CourseModule.status == 'active'
        ).count()

        if total_lectures == 0:
            return 0

        # Get completed and active progress records
        completed_lectures = Progress.query.filter_by(
            enrollment_id=enrollment_id,
            completed=True,
            status='active'
        ).count()

        return int((completed_lectures / total_lectures) * 100)
    
    @staticmethod
    def get_next_lecture(enrollment_id):
        """Get the next incomplete lecture resource for an enrollment"""
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            return None
        
        # Find first incomplete lecture
        incomplete_progress = Progress.query.filter_by(
            enrollment_id=enrollment_id,
            completed=False,
            status='active'
        ).first()
        
        if incomplete_progress:
            return LectureResource.query.get(incomplete_progress.lecture_resource_id)
        
        return None
