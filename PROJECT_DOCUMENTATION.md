# WPL Learning Platform - Project Documentation

**Last Updated:** December 30, 2025

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Database Architecture](#database-architecture)
4. [Backend Structure](#backend-structure)
5. [Frontend Structure](#frontend-structure)
6. [Key Features Implemented](#key-features-implemented)
7. [Recent Changes & Fixes](#recent-changes--fixes)
8. [How the Platform Works](#how-the-platform-works)
9. [User Accounts & Testing](#user-accounts--testing)
10. [Future Enhancements](#future-enhancements)

---

## 🎯 Project Overview

**WPL Learning Platform** is a comprehensive online learning management system (LMS) similar to Coursera/Udemy, built with modern web technologies. The platform enables instructors to create and manage courses with structured lectures and lessons, while students can enroll, learn, and track their progress.

### Core Concept
- **Completely FREE platform** - All courses are free with no pricing system
- **Course Structure:** Course → Lectures → Lessons (Video or Text)
- **Auto-counting system** - Number of lessons calculated automatically
- **11 Separate Database Modules** - Each feature has dedicated tables

---

## 🛠 Technology Stack

### Frontend
- **Framework:** Next.js 14.2.17 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** React Hooks (useState, useEffect)
- **Routing:** Next.js Dynamic Routes

### Backend
- **Framework:** Flask (Python)
- **ORM:** SQLAlchemy
- **Database:** MySQL
- **Migrations:** Flask-Migrate
- **Authentication:** Werkzeug (password hashing)
- **CORS:** Flask-CORS

### Development Tools
- **Package Manager:** npm (frontend), pip (backend)
- **Version Control:** Git
- **Code Editor:** VS Code

---

## 🗄 Database Architecture

### 11 Database Tables (One per Module)

#### 1. **users** (5 records)
- User authentication and basic info
- Fields: id, email, password, full_name, role (student/instructor)
- Roles: `student` or `instructor`

#### 2. **profiles** (5 records)
- Extended user profiles
- Fields: user_id (FK), bio, profile_picture, website, social_links (JSON), expertise (JSON), education (JSON)
- Contains professional info, social media, education history

#### 3. **courses** (4 records)
- Main course information
- Fields: id, instructor_id (FK), title, description, thumbnail, category, level, language, status
- **NO PRICE FIELDS** - All courses are free

#### 4. **course_details** (4 records)
- Detailed course information
- Fields: course_id (FK), requirements (JSON), who_is_for (JSON), objectives (JSON), syllabus (JSON), faq (JSON)
- Rich course metadata

#### 5. **course_categories** (6 records)
- Hierarchical category system
- Fields: id, name, slug, description, icon, parent_id (self-referencing FK)
- Categories: Data Science, Programming, Machine Learning, Web Development, Cloud Computing, Business

#### 6. **enrollments** (4 records)
- Student course enrollments
- Fields: id, user_id (FK), course_id (FK), progress, status, enrolled_at, completed_at
- Tracks enrollment status and completion

#### 7. **course_modules** / lectures (9 records)
- Course lecture modules
- Fields: id, course_id (FK), number, title, lessons (auto-calculated), duration
- **Lessons auto-count from lecture_resources**

#### 8. **lecture_resources** / lessons (0 records initially)
- Individual lessons within lectures
- Fields: id, lecture_id (FK), resource_type (video/text), title, url, content, duration, order
- Two types: **Video lessons** (YouTube/Vimeo links) or **Text lessons** (written content)

#### 9. **reviews** (4 records)
- Course reviews and comments
- Fields: id, course_id (FK), user_id (FK), rating, comment, created_at

#### 10. **ratings** (3 records)
- Course rating data
- Fields: id, course_id (FK), user_id (FK), rating, created_at

#### 11. **progress** (4 records)
- Detailed student progress tracking
- Fields: id, user_id (FK), course_id (FK), lecture_id (FK), completed_lectures (JSON), current_lecture, time_spent, notes (JSON)
- Tracks lecture-level progress with notes

### Database Relationships
```
users (1) ──→ (many) profiles
users (1) ──→ (many) courses (as instructor)
users (1) ──→ (many) enrollments
users (1) ──→ (many) reviews
users (1) ──→ (many) ratings
users (1) ──→ (many) progress

courses (1) ──→ (many) course_details
courses (1) ──→ (many) enrollments
courses (1) ──→ (many) course_modules/lectures
courses (1) ──→ (many) reviews
courses (1) ──→ (many) ratings
courses (1) ──→ (many) progress

course_modules/lectures (1) ──→ (many) lecture_resources/lessons
course_modules/lectures (1) ──→ (many) progress

course_categories (self-referencing for hierarchy)
```

---

## 🔧 Backend Structure

### Directory Structure
```
backend/
├── app.py                 # Flask app factory
├── config.py             # Configuration settings
├── database.py           # Database initialization
├── models.py             # All 11 SQLAlchemy models
├── seed_complete.py      # Original seed data
├── seed_new_tables.py    # Seed data for 4 new tables
└── routes/               # API endpoints (11 modules)
    ├── __init__.py       # Blueprint registration
    ├── users.py          # User authentication & management
    ├── profiles.py       # User profile CRUD
    ├── courses.py        # Course CRUD & search
    ├── course_details.py # Detailed course info
    ├── course_categories.py # Category management
    ├── enrollments.py    # Enrollment operations
    ├── lectures.py       # Lecture/module CRUD
    ├── lecture_resources.py # Lesson CRUD
    ├── reviews.py        # Course reviews
    ├── ratings.py        # Course ratings
    └── progress.py       # Progress tracking
```

### API Routes Structure
All routes prefixed with `/api/`

- **POST** `/api/users/register` - User registration
- **POST** `/api/users/login` - User login
- **GET** `/api/courses/` - Get all courses
- **GET** `/api/courses/search` - Search courses
- **POST** `/api/courses/` - Create course (instructor only)
- **GET** `/api/lectures/?course_id={id}` - Get course lectures
- **POST** `/api/lecture_resources/` - Add lesson
- **GET** `/api/lecture_resources/?lecture_id={id}` - Get lecture lessons
- ... (full CRUD for all 11 modules)

### Key Backend Features

#### 1. Auto-Counting Lessons
```python
# In models.py - CourseModule class
@property
def resource_count(self):
    """Get the number of resources for this lecture"""
    from models import LectureResource
    return LectureResource.query.filter_by(lecture_id=self.id).count()

def to_dict(self):
    actual_lessons = self.resource_count  # Auto-calculated
    return {
        'id': self.id,
        'lessons': actual_lessons,  # No manual input needed
        ...
    }
```

#### 2. Authentication System
- Password hashing with Werkzeug
- User ID stored in localStorage
- Sent via `X-User-Id` header in API requests

#### 3. Data Validation
- Required fields validated in routes
- Foreign key constraints enforced
- Unique constraints on user_course enrollments

---

## 🎨 Frontend Structure

### Directory Structure
```
frontend/src/app/
├── components/
│   ├── Header.tsx           # Navigation header
│   └── CourseCard.tsx       # Course display card
├── page.tsx                 # Homepage
├── dashboard/
│   └── page.tsx            # Student dashboard
├── courses/
│   └── page.tsx            # Browse courses
├── course/[id]/
│   └── page.tsx            # Course detail page
├── search/
│   └── page.tsx            # Search results
├── profile/
│   └── page.tsx            # User profile
└── instructor/
    └── courses/
        ├── new/
        │   └── page.tsx    # Create new course
        └── [id]/
            ├── edit/
            │   └── page.tsx    # Edit course
            └── lectures/
                ├── page.tsx    # Manage lectures
                └── [lectureId]/
                    └── lessons/
                        └── page.tsx  # Manage lessons (video/text)
```

### Frontend API Client (`lib/api.ts`)

Three main API clients:

#### 1. **lectureApi**
```typescript
{
  createLecture(course_id, number, title, duration)
  getCourseLectures(courseId)
  getLecture(lectureId)
  updateLecture(lectureId, updates)
  deleteLecture(lectureId)
}
```

#### 2. **lectureResourceApi** (Used for lessons)
```typescript
{
  createResource(lecture_id, resource_type, title, url, content, duration, order)
  getLectureResources(lectureId)
  getResource(resourceId)
  updateResource(resourceId, updates)
  deleteResource(resourceId)
}
```

#### 3. **progressApi**
```typescript
{
  createProgress(enrollmentId, progress)
  getProgress(enrollmentId)
  getUserProgress(userId)
  updateProgress(enrollmentId, progress)
  resetProgress(enrollmentId)
}
```

---

## ✨ Key Features Implemented

### For Students
1. **Browse Courses** - View all available courses
2. **Search & Filter** - Search by title, category, level
3. **Course Details** - View full course information with objectives, requirements, syllabus
4. **Enroll in Courses** - One-click enrollment (all courses free)
5. **Dashboard** - View enrolled courses and progress
6. **Progress Tracking** - Track completed lectures and time spent
7. **Leave Reviews** - Rate and review completed courses
8. **User Profile** - View and edit profile information

### For Instructors
1. **Create Courses** - Full course creation with rich details
2. **Edit Courses** - Update course information anytime
3. **Manage Lectures** - Add/edit/delete lecture modules
4. **Manage Lessons** - Add video or text lessons to each lecture
5. **Auto Lesson Counting** - Lessons counted automatically as you add them
6. **Course Dashboard** - View all created courses
7. **Delete Courses** - Remove courses with confirmation

### Smart Features
1. **Auto-Count System**
   - Number of lessons automatically calculated
   - Updates in real-time as lessons are added/removed
   - No manual input needed

2. **Two Lesson Types**
   - **Video Lessons:** YouTube, Vimeo, or direct video links
   - **Text Lessons:** Written content with rich text area

3. **Hierarchical Structure**
   - Course → Lectures (modules) → Lessons (resources)
   - Each level properly linked with foreign keys

4. **Free Platform**
   - No pricing anywhere in the system
   - All price-related code removed

---

## 🔄 Recent Changes & Fixes

### Phase 1: Image Configuration Fix
**Problem:** Next.js error for picsum.photos images  
**Solution:** Added `picsum.photos` to `next.config.mjs` remotePatterns

### Phase 2: Complete Price Removal
**Problem:** User wanted all courses free  
**Changes Made:**
- ✅ Removed `price` and `original_price` from Course model
- ✅ Removed price fields from courses.py routes
- ✅ Removed price from seed_complete.py
- ✅ Removed price display from all frontend pages:
  - CourseCard.tsx
  - course/[id]/page.tsx
  - dashboard/page.tsx
  - profile/page.tsx
  - search/page.tsx
  - courses/page.tsx
  - instructor forms

### Phase 3: Database Table Expansion
**Problem:** Some modules shared tables instead of having dedicated ones  
**Solution:** Created 4 new models and tables:
- ✅ Profile (extended user data)
- ✅ CourseDetail (detailed course info)
- ✅ CourseCategory (category hierarchy)
- ✅ Progress (detailed progress tracking)
- ✅ Ran `db.create_all()` to create all 11 tables

### Phase 4: Lecture Resources Implementation
**Problem:** LectureResource had only placeholder routes  
**Solution:**
- ✅ Created LectureResource model with full schema
- ✅ Implemented all CRUD operations in lecture_resources.py
- ✅ Added frontend API integration
- ✅ Created management UI pages

### Phase 5: Instructor Content Management UI
**Problem:** No way for instructors to manage lectures/lessons  
**Solution:**
- ✅ Created `/instructor/courses/[id]/lectures/page.tsx` - Manage lectures
- ✅ Created `/instructor/courses/[id]/lectures/[lectureId]/lessons/page.tsx` - Manage lessons
- ✅ Added "Manage Lectures" button to course edit page
- ✅ Renamed from "Resources" to "Lessons" for clarity

### Phase 6: Seed Data Population
**Problem:** 4 new tables had no data  
**Solution:**
- ✅ Created seed_new_tables.py script
- ✅ Added 5 user profiles with bio, expertise, education, social links
- ✅ Added 6 course categories (4 parent + 2 child)
- ✅ Added 4 detailed course information records
- ✅ Added 4 student progress records

### Phase 7: Auto-Count Lessons System
**Problem:** Manual lesson input caused inconsistencies  
**Solution:**
- ✅ Added `resource_count` property to CourseModule model
- ✅ Modified `to_dict()` to return calculated count
- ✅ Removed manual "lessons" input from frontend form
- ✅ Added informative note about auto-calculation
- ✅ Lessons now update automatically when added/removed

### Phase 8: Route & Naming Fixes
**Problem:** 404 errors and confusing terminology  
**Solution:**
- ✅ Fixed route parameter inconsistency ([courseId] → [id])
- ✅ Moved resources page to correct folder structure
- ✅ Renamed "Resources" to "Lessons" throughout
- ✅ Changed resource_type to lesson_type in UI
- ✅ Simplified to two lesson types: video and text

### Bug Fixes
1. ✅ **Link Import Error** - Added missing `import Link from 'next/link'`
2. ✅ **Missing IDs in API** - Fixed CourseModule.to_dict() to return id and course_id
3. ✅ **404 Route Error** - Standardized parameter naming across pages
4. ✅ **Foreign Key Constraints** - Fixed seed data to use correct IDs
5. ✅ **Category Hierarchy** - Parent categories inserted before child categories

---

## 🎓 How the Platform Works

### User Flow

#### 1. Student Journey
```
Register/Login
    ↓
Browse Courses (homepage/courses page)
    ↓
View Course Details (click on course)
    ↓
Enroll in Course (click "Enroll Now")
    ↓
Access Course Content
    ↓
Watch Video Lessons / Read Text Lessons
    ↓
Track Progress
    ↓
Complete Course
    ↓
Leave Review & Rating
```

#### 2. Instructor Journey
```
Register/Login as Instructor
    ↓
Dashboard → Create New Course
    ↓
Fill Course Details
    ↓
Click "Manage Lectures"
    ↓
Add Lecture Modules
    ↓
Click "Manage Lessons" for each lecture
    ↓
Add Video or Text Lessons
    ↓
Lessons Auto-Count
    ↓
Course Published
    ↓
Students Can Enroll
```

### Course Structure Example

```
📚 Complete Data Science Bootcamp (Course)
│
├── 📖 Module 1: Python Basics (Lecture)
│   ├── 🎥 Lesson 1: Introduction to Python (Video)
│   ├── 📝 Lesson 2: Variables and Data Types (Text)
│   ├── 🎥 Lesson 3: Control Flow (Video)
│   └── 📝 Lesson 4: Practice Exercises (Text)
│   [Lessons: 4 - Auto-counted]
│
├── 📖 Module 2: Data Analysis (Lecture)
│   ├── 🎥 Lesson 1: NumPy Introduction (Video)
│   ├── 🎥 Lesson 2: Pandas Basics (Video)
│   └── 📝 Lesson 3: Data Cleaning Guide (Text)
│   [Lessons: 3 - Auto-counted]
│
└── 📖 Module 3: Machine Learning (Lecture)
    ├── 🎥 Lesson 1: ML Overview (Video)
    ├── 📝 Lesson 2: Algorithms Explained (Text)
    ├── 🎥 Lesson 3: Scikit-learn Tutorial (Video)
    ├── 🎥 Lesson 4: Model Evaluation (Video)
    └── 📝 Lesson 5: Best Practices (Text)
    [Lessons: 5 - Auto-counted]

Total Course Lessons: 12 (automatically calculated)
```

### Lesson Types Explained

#### 🎥 Video Lessons
- Instructor provides URL (YouTube, Vimeo, direct link)
- Students watch embedded videos
- Track watch time and progress
- Example: "Introduction to Python - 45 min tutorial"

#### 📝 Text Lessons
- Instructor writes content directly
- Students read educational material
- Can include code examples, explanations
- Example: "Understanding Variables - Complete guide with examples"

---

## 👥 User Accounts & Testing

### Test Accounts (Seeded in Database)

#### Students
1. **Email:** student1@test.com  
   **Password:** password123  
   **Enrollments:** Data Science Bootcamp, Advanced ML

2. **Email:** student2@test.com  
   **Password:** password123  
   **Enrollments:** Data Science Bootcamp, React Guide

#### Instructors
3. **Email:** yawar@iqra.com  
   **Password:** password123  
   **Courses:** Complete Data Science Bootcamp, Advanced Machine Learning  
   **Profile:** PhD in Computer Science, 10+ years experience

4. **Email:** balti@yahoo.com  
   **Password:** password123  
   **Courses:** React Complete Guide 2024  
   **Profile:** Full-stack developer, MS in Software Engineering

5. **Email:** meta@facebook.com  
   **Password:** password123  
   **Role:** Student

### Sample Course Data

#### Course 1: Complete Data Science Bootcamp
- **Instructor:** yawar@iqra.com
- **Category:** Data Science
- **Level:** Beginner
- **Lectures:** 3 (Python Basics, Data Analysis, ML Fundamentals)
- **Status:** Published

#### Course 2: Advanced Machine Learning
- **Instructor:** yawar@iqra.com
- **Category:** Machine Learning
- **Level:** Advanced
- **Lectures:** 3 (Neural Networks, Deep Learning, Advanced Topics)
- **Status:** Published

#### Course 3: React Complete Guide 2024
- **Instructor:** balti@yahoo.com
- **Category:** Web Development
- **Level:** Intermediate
- **Lectures:** 4 (React Fundamentals, Hooks, Advanced Patterns, etc.)
- **Status:** Published

#### Course 4: Python for Beginners
- **Instructor:** balti@yahoo.com
- **Category:** Programming
- **Level:** Beginner
- **Status:** Published

---

## 🚀 Running the Platform

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
# Runs on http://127.0.0.1:5001
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### Database Setup
```bash
# Create database
mysql -u root -p
CREATE DATABASE wpl_coursera;

# Run migrations
cd backend
flask db upgrade

# Seed data
python seed_complete.py
python seed_new_tables.py
```

---

## 🔮 Future Enhancements

### Planned Features
1. **Video Player Integration** - Embedded video player with progress tracking
2. **Certificate Generation** - PDF certificates on course completion
3. **Discussion Forums** - Student-instructor Q&A per course
4. **Assignments & Quizzes** - Assessments within lessons
5. **Live Sessions** - Scheduled live classes with Zoom integration
6. **Course Preview** - Free preview lessons before enrollment
7. **Wishlists** - Save courses for later
8. **Notifications** - Email/push notifications for updates
9. **Course Bundles** - Group related courses
10. **Analytics Dashboard** - Instructor course statistics

### Potential Improvements
- Dark mode theme
- Mobile app (React Native)
- Advanced search filters (duration, rating, etc.)
- Course recommendations based on interests
- Social features (follow instructors, share progress)
- Multi-language support
- Downloadable resources (PDFs, code files)
- Note-taking within lessons
- Bookmarks for important lessons
- Speed controls for video playback

---

## 📊 Project Statistics

- **Total Database Tables:** 11
- **Total Seed Records:** 40+ across all tables
- **Backend Routes:** 50+ API endpoints
- **Frontend Pages:** 15+ pages
- **Models:** 11 SQLAlchemy models
- **API Modules:** 11 Flask blueprints
- **Course Structure Levels:** 3 (Course → Lecture → Lesson)
- **User Roles:** 2 (Student, Instructor)
- **Lesson Types:** 2 (Video, Text)
- **Lines of Code:** ~10,000+ (estimated)

---

## 🏆 Key Achievements

✅ **Complete Database Redesign** - 11 separate tables with proper relationships  
✅ **Free Platform** - Removed all pricing completely  
✅ **Auto-Counting System** - Smart lesson calculation  
✅ **Dual Lesson Types** - Video and text content support  
✅ **Full CRUD Operations** - All modules have complete create/read/update/delete  
✅ **Instructor Tools** - Comprehensive course management UI  
✅ **Progress Tracking** - Detailed student progress with notes  
✅ **Seed Data** - Complete test data for all tables  
✅ **Modern Stack** - Next.js 14 + Flask + MySQL  
✅ **Type Safety** - TypeScript on frontend  

---

## 📝 Notes

- All courses are **completely free** - no payment system
- Lesson count is **automatically calculated** - never manually entered
- Two lesson types only: **Video** (URL) and **Text** (content)
- Route structure: `/instructor/courses/[id]/lectures/[lectureId]/lessons`
- Database uses **foreign keys** for referential integrity
- Authentication via **localStorage** and **X-User-Id** header
- Images hosted on **Unsplash** and **Picsum**

---

## 📧 Contact & Support

For questions or issues:
- Review this documentation
- Check database structure diagrams
- Test with provided user accounts
- Verify API endpoints are running

---

**End of Documentation**

*This platform represents a fully functional online learning management system with modern architecture, comprehensive features, and a focus on user experience.*
