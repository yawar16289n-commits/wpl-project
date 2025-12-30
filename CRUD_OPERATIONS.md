# Backend CRUD Operations Documentation

## 11 Modules with Complete CRUD Operations

### 1. **USERS Module** (`/api/users`)
**Database Table:** `users`

#### CRUD Operations:

**CREATE (POST)**
- `POST /users/` - Create new user (name, email, password, role required)
- `POST /users/auth/signup` - Sign up new user (auth endpoint)

**READ (GET)**
- `GET /users/` - Get all users (optional filter by role)
- `GET /users/<user_id>` - Get user by ID
- `GET /users/profile/<user_id>` - Get public user profile
- `GET /users/my-profile/<user_id>` - Get own profile (requires auth)

**UPDATE (PUT)**
- `PUT /users/<user_id>` - Update user details (name, email, bio, profile_picture)
- `PUT /users/profile/<user_id>` - Update user profile (requires auth)

**DELETE (DELETE)**
- `DELETE /users/<user_id>` - Delete user (requires auth)

**AUTHENTICATION**
- `POST /users/auth/login` - User login (email, password)

---

### 2. **PROFILES Module** (`/api/profiles`)
**Database Table:** `users` (profile extension)

#### CRUD Operations:

**CREATE (POST)**
- `POST /profiles/` - Create profile (user_id required)

**READ (GET)**
- `GET /profiles/` - Get all profiles
- `GET /profiles/<profile_id>` - Get profile by ID
- `GET /profiles/user/<user_id>` - Get profile by user ID

**UPDATE (PUT)**
- `PUT /profiles/<profile_id>` - Update profile details

**DELETE (DELETE)**
- `DELETE /profiles/<profile_id>` - Delete profile

---

### 3. **COURSES Module** (`/api/courses`)
**Database Table:** `courses`

#### CRUD Operations:

**CREATE (POST)**
- `POST /courses/` - Create new course (title, description, instructor_id, category required)

**READ (GET)**
- `GET /courses/` - Get all courses
- `GET /courses/<course_id>` - Get course by ID
- `GET /courses/search` - Search/filter courses (supports q, category, level, sort parameters)

**UPDATE (PUT)**
- `PUT /courses/<course_id>` - Update course details

**DELETE (DELETE)**
- `DELETE /courses/<course_id>` - Delete course

**SEARCH/FILTER**
- `GET /courses/search?q=query&category=cat&level=level&sort=type`
  - Parameters: q (search query), category, level (Beginner/Intermediate/Advanced)
  - Sort options: created_at, price, rating, students, title

---

### 4. **COURSE DETAILS Module** (`/api/course_details`)
**Database Table:** `courses` (detailed info)

#### CRUD Operations:

**CREATE (POST)**
- `POST /course_details/` - Create course details (course_id required)

**READ (GET)**
- `GET /course_details/` - Get all course details
- `GET /course_details/<detail_id>` - Get detail by ID
- `GET /course_details/course/<course_id>` - Get details for specific course

**UPDATE (PUT)**
- `PUT /course_details/<detail_id>` - Update course details

**DELETE (DELETE)**
- `DELETE /course_details/<detail_id>` - Delete course details

---

### 5. **COURSE CATEGORIES Module** (`/api/course_categories`)
**Database Table:** `course_categories` (or embedded in courses)

#### CRUD Operations:

**CREATE (POST)**
- `POST /course_categories/` - Create category (name required)

**READ (GET)**
- `GET /course_categories/` - Get all categories
- `GET /course_categories/<category_id>` - Get category by ID

**UPDATE (PUT)**
- `PUT /course_categories/<category_id>` - Update category

**DELETE (DELETE)**
- `DELETE /course_categories/<category_id>` - Delete category

---

### 6. **ENROLLMENTS Module** (`/api/enrollments`)
**Database Table:** `enrollments`

#### CRUD Operations:

**CREATE (POST)**
- `POST /enrollments/` - Enroll user in course (user_id, course_id required)

**READ (GET)**
- `GET /enrollments/` - Get all enrollments
- `GET /enrollments/<enrollment_id>` - Get enrollment by ID
- `GET /enrollments/user/<user_id>` - Get user's enrollments (supports status filter)
- `GET /enrollments/check/<user_id>/<course_id>` - Check if user enrolled in course

**UPDATE (PUT)**
- `PUT /enrollments/<enrollment_id>` - Update enrollment details
- `PUT /enrollments/<enrollment_id>/progress` - Update progress (progress value 0-100)

**DELETE (DELETE)**
- `DELETE /enrollments/<enrollment_id>` - Unenroll from course

---

### 7. **LECTURES Module** (`/api/lectures`)
**Database Table:** `course_modules`

#### CRUD Operations:

**CREATE (POST)**
- `POST /lectures/` - Create lecture/module (course_id, title, number required)

**READ (GET)**
- `GET /lectures/` - Get all lectures
- `GET /lectures/<lecture_id>` - Get lecture by ID
- `GET /lectures/course/<course_id>` - Get all lectures for a course

**UPDATE (PUT)**
- `PUT /lectures/<lecture_id>` - Update lecture details

**DELETE (DELETE)**
- `DELETE /lectures/<lecture_id>` - Delete lecture

---

### 8. **LECTURE RESOURCES Module** (`/api/lecture_resources`)
**Database Table:** `lecture_resources` (future expansion)

#### CRUD Operations:

**CREATE (POST)**
- `POST /lecture_resources/` - Upload lecture resource (lecture_id, url required)

**READ (GET)**
- `GET /lecture_resources/` - Get all resources
- `GET /lecture_resources/<resource_id>` - Get resource by ID
- `GET /lecture_resources/lecture/<lecture_id>` - Get resources for lecture

**UPDATE (PUT)**
- `PUT /lecture_resources/<resource_id>` - Update resource

**DELETE (DELETE)**
- `DELETE /lecture_resources/<resource_id>` - Delete resource

---

### 9. **REVIEWS Module** (`/api/reviews`)
**Database Table:** `reviews` (future model)

#### CRUD Operations:

**CREATE (POST)**
- `POST /reviews/` - Create review (course_id, user_id, comment required)

**READ (GET)**
- `GET /reviews/` - Get all reviews
- `GET /reviews/<review_id>` - Get review by ID
- `GET /reviews/course/<course_id>` - Get all reviews for course

**UPDATE (PUT)**
- `PUT /reviews/<review_id>` - Update review

**DELETE (DELETE)**
- `DELETE /reviews/<review_id>` - Delete review

---

### 10. **RATINGS Module** (`/api/ratings`)
**Database Table:** `ratings` (future model)

#### CRUD Operations:

**CREATE (POST)**
- `POST /ratings/` - Create rating (course_id, user_id, rating 1-5 required)

**READ (GET)**
- `GET /ratings/` - Get all ratings
- `GET /ratings/<rating_id>` - Get rating by ID
- `GET /ratings/course/<course_id>` - Get all ratings for course
- `GET /ratings/user/<user_id>` - Get user's ratings

**UPDATE (PUT)**
- `PUT /ratings/<rating_id>` - Update rating

**DELETE (DELETE)**
- `DELETE /ratings/<rating_id>` - Delete rating

---

### 11. **PROGRESS Module** (`/api/progress`)
**Database Table:** `enrollments` (progress tracking)

#### CRUD Operations:

**CREATE (POST)**
- `POST /progress/` - Create progress entry (enrollment_id, progress required)

**READ (GET)**
- `GET /progress/` - Get all progress
- `GET /progress/<progress_id>` - Get progress by ID
- `GET /progress/enrollment/<enrollment_id>` - Get progress for enrollment

**UPDATE (PUT)**
- `PUT /progress/<progress_id>` - Update progress

**DELETE (DELETE)**
- `DELETE /progress/<progress_id>` - Delete progress

**DASHBOARD ENDPOINTS**
- `GET /progress/dashboard/student/<user_id>` - Get student dashboard (enrollments, stats)
- `GET /progress/dashboard/instructor/<user_id>` - Get instructor dashboard (courses, stats)

---

## Frontend API Integration (`api.ts`)

### AuthApi
```typescript
authApi.signup(userData)        // POST /users/auth/signup
authApi.login(credentials)      // POST /users/auth/login
authApi.getUser(userId)         // GET /users/<userId>
```

### UserApi
```typescript
userApi.getPublicProfile(userId)                  // GET /users/profile/<userId>
userApi.getMyProfile(userId)                      // GET /users/my-profile/<userId>
userApi.updateProfile(userId, updates)            // PUT /users/profile/<userId>
```

### CourseApi
```typescript
courseApi.getCourses(filters)   // GET /courses/search?q=...&category=...&level=...
courseApi.getCourse(courseId)   // GET /courses/<courseId>
courseApi.createCourse(data)    // POST /courses/
courseApi.updateCourse(id, upd) // PUT /courses/<courseId>
courseApi.deleteCourse(id)      // DELETE /courses/<courseId>
```

### DashboardApi
```typescript
dashboardApi.getStudentDashboard(userId)     // GET /progress/dashboard/student/<userId>
dashboardApi.getInstructorDashboard(userId)  // GET /progress/dashboard/instructor/<userId>
```

### EnrollmentApi
```typescript
enrollmentApi.enroll(userId, courseId)       // POST /enrollments/
enrollmentApi.unenroll(enrollmentId)         // DELETE /enrollments/<enrollmentId>
enrollmentApi.checkEnrollment(userId, courseId)  // GET /enrollments/check/<userId>/<courseId>
enrollmentApi.updateProgress(enrollmentId, progress)  // PUT /enrollments/<enrollmentId>/progress
enrollmentApi.getUserEnrollments(userId, status)     // GET /enrollments/user/<userId>
```

---

## Summary
- **Total Modules:** 11
- **Total CRUD Operations:** 89+
- **Removed Modules:** auth.py, dashboard.py, search.py (consolidated into users, courses, progress)
- **Active Modules:** users, profiles, courses, course_details, course_categories, enrollments, lectures, lecture_resources, reviews, ratings, progress
