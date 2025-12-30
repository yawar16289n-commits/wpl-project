const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

function getUserIdFromStorage(): string | null {
  if (typeof window === 'undefined') return null;
  const user = localStorage.getItem('user');
  if (!user) return null;
  try {
    const userData = JSON.parse(user);
    return userData.id?.toString() || null;
  } catch {
    return null;
  }
}

async function apiCall<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const userId = getUserIdFromStorage();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };
    
    if (userId) {
      headers['X-User-Id'] = userId;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers,
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.error || 'Something went wrong',
      };
    }

    return {
      success: true,
      data,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

export const authApi = {
  signup: async (userData: {
    name: string;
    email: string;
    password: string;
    role: 'learner' | 'instructor';
  }) => {
    return apiCall('/users/auth/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  login: async (credentials: { email: string; password: string }) => {
    return apiCall('/users/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  getUser: async (userId: number) => {
    return apiCall(`/users/${userId}`, {
      method: 'GET',
    });
  },
};

export const userApi = {
  getPublicProfile: async (userId: number) => {
    return apiCall(`/users/profile/${userId}`, {
      method: 'GET',
    });
  },

  getMyProfile: async (userId: number) => {
    return apiCall(`/users/my-profile/${userId}`, {
      method: 'GET',
    });
  },

  updateProfile: async (
    userId: number,
    updates: { name?: string; bio?: string; profile_picture?: string }
  ) => {
    return apiCall(`/users/profile/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },
};

export const courseApi = {
  getCourses: async (filters?: {
    category?: string;
    level?: string;
    q?: string;
  }) => {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.level) params.append('level', filters.level);
    if (filters?.q) params.append('q', filters.q);

    const query = params.toString() ? `?${params.toString()}` : '';
    return apiCall(`/courses/search${query}`, {
      method: 'GET',
    });
  },

  getCourse: async (courseId: number) => {
    return apiCall(`/courses/${courseId}`, {
      method: 'GET',
    });
  },

  createCourse: async (courseData: any) => {
    return apiCall('/courses/', {
      method: 'POST',
      body: JSON.stringify(courseData),
    });
  },

  updateCourse: async (courseId: number, updates: any) => {
    return apiCall(`/courses/${courseId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  deleteCourse: async (courseId: number) => {
    return apiCall(`/courses/${courseId}`, {
      method: 'DELETE',
    });
  },
};

export const dashboardApi = {
  getStudentDashboard: async (userId: number) => {
    return apiCall(`/progress/dashboard/student/${userId}`, {
      method: 'GET',
    });
  },

  getInstructorDashboard: async (userId: number) => {
    return apiCall(`/progress/dashboard/instructor/${userId}`, {
      method: 'GET',
    });
  },
};

export const enrollmentApi = {
  enroll: async (userId: number, courseId: number) => {
    return apiCall('/enrollments/', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, course_id: courseId }),
    });
  },

  unenroll: async (enrollmentId: number) => {
    return apiCall(`/enrollments/${enrollmentId}`, {
      method: 'DELETE',
    });
  },

  checkEnrollment: async (userId: number, courseId: number) => {
    return apiCall(`/enrollments/check/${userId}/${courseId}`, {
      method: 'GET',
    });
  },

  updateProgress: async (enrollmentId: number, progress: number) => {
    return apiCall(`/enrollments/${enrollmentId}/progress`, {
      method: 'PUT',
      body: JSON.stringify({ progress }),
    });
  },

  getUserEnrollments: async (userId: number, status?: string) => {
    const query = status ? `?status=${status}` : '';
    return apiCall(`/enrollments/user/${userId}${query}`, {
      method: 'GET',
    });
  },
};

export const reviewApi = {
  createReview: async (courseId: number, userId: number, comment: string) => {
    return apiCall('/reviews/', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId, user_id: userId, comment }),
    });
  },

  getCourseReviews: async (courseId: number) => {
    return apiCall(`/reviews/course/${courseId}`, {
      method: 'GET',
    });
  },

  updateReview: async (reviewId: number, comment: string) => {
    return apiCall(`/reviews/${reviewId}`, {
      method: 'PUT',
      body: JSON.stringify({ comment }),
    });
  },

  deleteReview: async (reviewId: number) => {
    return apiCall(`/reviews/${reviewId}`, {
      method: 'DELETE',
    });
  },
};

export const ratingApi = {
  createRating: async (courseId: number, userId: number, rating: number) => {
    return apiCall('/ratings/', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId, user_id: userId, rating }),
    });
  },

  getCourseRatings: async (courseId: number) => {
    return apiCall(`/ratings/course/${courseId}`, {
      method: 'GET',
    });
  },

  getUserRating: async (userId: number, courseId: number) => {
    return apiCall(`/ratings/user/${userId}?course_id=${courseId}`, {
      method: 'GET',
    });
  },

  updateRating: async (ratingId: number, rating: number) => {
    return apiCall(`/ratings/${ratingId}`, {
      method: 'PUT',
      body: JSON.stringify({ rating }),
    });
  },

  deleteRating: async (ratingId: number) => {
    return apiCall(`/ratings/${ratingId}`, {
      method: 'DELETE',
    });
  },
};

export const lectureApi = {
  createLecture: async (lectureData: {
    course_id: number;
    number: number;
    title: string;
    lessons?: number;
    duration?: string;
  }) => {
    return apiCall('/lectures/', {
      method: 'POST',
      body: JSON.stringify(lectureData),
    });
  },

  getCourseLectures: async (courseId: number) => {
    return apiCall(`/lectures/?course_id=${courseId}`, {
      method: 'GET',
    });
  },

  getLecture: async (lectureId: number) => {
    return apiCall(`/lectures/${lectureId}`, {
      method: 'GET',
    });
  },

  updateLecture: async (lectureId: number, updates: any) => {
    return apiCall(`/lectures/${lectureId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  deleteLecture: async (lectureId: number) => {
    return apiCall(`/lectures/${lectureId}`, {
      method: 'DELETE',
    });
  },
};

export const lectureResourceApi = {
  createResource: async (resourceData: {
    lecture_id: number;
    resource_type: 'video' | 'pdf' | 'link' | 'document' | 'quiz';
    title: string;
    url?: string;
    content?: string;
    duration?: string;
    order?: number;
  }) => {
    return apiCall('/lecture-resources/', {
      method: 'POST',
      body: JSON.stringify(resourceData),
    });
  },

  getLectureResources: async (lectureId: number) => {
    return apiCall(`/lecture-resources/?lecture_id=${lectureId}`, {
      method: 'GET',
    });
  },

  getResource: async (resourceId: number) => {
    return apiCall(`/lecture-resources/${resourceId}`, {
      method: 'GET',
    });
  },

  updateResource: async (resourceId: number, updates: any) => {
    return apiCall(`/lecture-resources/${resourceId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  deleteResource: async (resourceId: number) => {
    return apiCall(`/lecture-resources/${resourceId}`, {
      method: 'DELETE',
    });
  },
};

export const progressApi = {
  createProgress: async (enrollmentId: number, progress: number) => {
    return apiCall('/progress/', {
      method: 'POST',
      body: JSON.stringify({ enrollment_id: enrollmentId, progress }),
    });
  },

  getProgress: async (enrollmentId: number) => {
    return apiCall(`/progress/${enrollmentId}`, {
      method: 'GET',
    });
  },

  getUserProgress: async (userId: number) => {
    return apiCall(`/progress/?user_id=${userId}`, {
      method: 'GET',
    });
  },

  updateProgress: async (enrollmentId: number, progress: number) => {
    return apiCall(`/progress/${enrollmentId}`, {
      method: 'PUT',
      body: JSON.stringify({ progress }),
    });
  },

  resetProgress: async (enrollmentId: number) => {
    return apiCall(`/progress/${enrollmentId}`, {
      method: 'DELETE',
    });
  },
};

export { API_BASE_URL };
