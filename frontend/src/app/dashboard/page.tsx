'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/app/components/Header';
import { dashboardApi, adminApi } from '@/lib/api';

interface CourseData {
  id: number;
  title: string;
  description: string;
  instructor?: string;
  instructor_id?: number;
  company?: string;
  image: string;
  rating: number;
  students: number;
  level: string;
  duration: string;
  category?: string;
}

interface EnrollmentData {
  id: number;
  user_id: number;
  course_id: number;
  enrolled_at: string;
  progress: number;
  status: string;
  course: CourseData;
}

interface DashboardData {
  user: {
    id: number;
    name: string;
    email: string;
    role: string;
  };
  enrolled_courses?: {
    in_progress: EnrollmentData[];
    completed: EnrollmentData[];
  };
  created_courses?: {
    published: CourseData[];
    drafts: CourseData[];
  };
  stats: {
    total_enrolled?: number;
    in_progress?: number;
    completed?: number;
    total_courses?: number;
    published?: number;
    drafts?: number;
    total_students?: number;
    total_reviews?: number;
    total_lecturers?: number;
    total_enrollments?: number;
  };
}

interface UserData {
  id: number;
  name: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
}

// Helper function to validate and sanitize image URLs
const getValidImageUrl = (url: string | null | undefined): string => {
  if (!url) return '/placeholder.svg';
  
  try {
    const urlObj = new URL(url);
    const allowedHosts = ['images.unsplash.com', 'unsplash.com', 'picsum.photos'];
    
    if (allowedHosts.includes(urlObj.hostname)) {
      return url;
    }
  } catch (e) {
    // Invalid URL, return placeholder
  }
  
  return '/placeholder.svg';
};

export default function Dashboard() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('inprogress');
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUnenrollModal, setShowUnenrollModal] = useState(false);
  const [selectedEnrollment, setSelectedEnrollment] = useState<EnrollmentData | null>(null);
  const [unenrolling, setUnenrolling] = useState(false);
  const [showDeleteCourseModal, setShowDeleteCourseModal] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<CourseData | null>(null);
  const [deletingCourse, setDeletingCourse] = useState(false);
  
  // Admin-specific states
  const [users, setUsers] = useState<UserData[]>([]);
  const [userFilter, setUserFilter] = useState('active');
  const [showDeleteUserModal, setShowDeleteUserModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
  const [deletingUser, setDeletingUser] = useState(false);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          setError('Please log in to view your dashboard');
          return;
        }

        const user = JSON.parse(userStr);
        const userId = user.id;
        const userRole = user.role;

        let response;
        if (userRole === 'admin') {
          response = await adminApi.getDashboardStats();
        } else if (userRole === 'instructor') {
          response = await dashboardApi.getInstructorDashboard(userId);
        } else {
          response = await dashboardApi.getStudentDashboard(userId);
        }

        if (response.success && response.data) {
          // Dashboard API returns data directly, not nested in 'dashboard'
          const data = response.data as any;
          
          // Transform the admin dashboard response
          if (userRole === 'admin' && data.stats) {
            const transformedData: DashboardData = {
              user: user,
              stats: data.stats
            };
            setDashboardData(transformedData);
          } else if (userRole !== 'instructor' && userRole !== 'admin' && data.courses) {
            // Map API response to component format
            const mappedCourses = data.courses.map((item: any) => ({
              id: item.enrollment_id,
              user_id: userId,
              course_id: item.course.id,
              enrolled_at: item.enrolled_at,
              progress: item.progress_percentage, // API returns progress_percentage
              status: item.status,
              course: item.course
            }));
            
            const transformedData: DashboardData = {
              user: user,
              enrolled_courses: {
                in_progress: mappedCourses.filter((c: any) => c.status === 'active'),
                completed: mappedCourses.filter((c: any) => c.status === 'completed')
              },
              stats: {
                total_enrolled: data.total || 0,
                in_progress: mappedCourses.filter((c: any) => c.status === 'active').length,
                completed: mappedCourses.filter((c: any) => c.status === 'completed').length
              }
            };
            setDashboardData(transformedData);
          } else if (userRole === 'instructor' && data.courses) {
            // Transform instructor dashboard
            const transformedData: DashboardData = {
              user: user,
              created_courses: {
                published: data.courses
                  .filter((item: any) => item.course?.status === 'active')
                  .map((item: any) => ({
                    id: item.course.id,
                    title: item.course.title,
                    description: item.course.description,
                    level: item.course.level,
                    duration: item.course.duration,
                    image: item.course.image,
                    status: item.course.status,
                    students: item.total_students,
                    rating: item.rating
                  })),
                drafts: data.courses
                  .filter((item: any) => item.course?.status === 'unpublished')
                  .map((item: any) => ({
                    id: item.course.id,
                    title: item.course.title,
                    description: item.course.description,
                    level: item.course.level,
                    duration: item.course.duration,
                    image: item.course.image,
                    status: item.course.status,
                    students: item.total_students,
                    rating: item.rating
                  }))
              },
              stats: {
                total_courses: data.total || 0,
                published: data.courses.filter((item: any) => item.course?.status === 'active').length,
                drafts: data.courses.filter((item: any) => item.course?.status === 'unpublished').length,
                total_students: data.courses.reduce((sum: number, item: any) => sum + (item.total_students || 0), 0),
                total_reviews: data.courses.reduce((sum: number, item: any) => sum + (item.total_reviews || 0), 0)
              }
            };
            setDashboardData(transformedData);
          } else {
            setDashboardData(data);
          }

        } else {
          setError(response.error || 'Failed to load dashboard');
        }
      } catch (err) {
        console.error('Error fetching dashboard:', err);
        setError('Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  // Admin: Fetch users
  const fetchUsers = async () => {
    try {
      const userStr = localStorage.getItem('user');
      if (!userStr) return;
      
      const user = JSON.parse(userStr);
      console.log('Fetching users with filter:', userFilter, 'Admin ID:', user.id);
      const usersRes = await adminApi.getAllUsers(userFilter, user.id);
      console.log('Users response:', usersRes);
      if (usersRes.success && usersRes.data) {
        const userData = usersRes.data as { users: UserData[] };
        console.log('Setting users:', userData.users);
        setUsers(userData.users);
      } else {
        console.error('Failed to fetch users:', usersRes.error);
      }
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  };

  // Admin: Watch user filter changes and fetch users when dashboard loads
  useEffect(() => {
    if (dashboardData?.user?.role === 'admin') {
      fetchUsers();
    }
  }, [userFilter, dashboardData]);

  // Admin: Delete user handler
  const handleDeleteUser = async () => {
    if (!selectedUser || !dashboardData) return;

    setDeletingUser(true);
    const response = await adminApi.deleteUser(selectedUser.id, dashboardData.user.id);

    if (response.success) {
      setShowDeleteUserModal(false);
      setSelectedUser(null);
      fetchUsers();
    } else {
      alert(response.error || 'Failed to delete user');
    }
    setDeletingUser(false);
  };

  const handleUnenrollClick = (enrollment: EnrollmentData) => {
    setSelectedEnrollment(enrollment);
    setShowUnenrollModal(true);
  };

  const handleContinueLearning = async (enrollment: EnrollmentData) => {
    // Simply navigate to the course learning page
    window.location.href = `/learn/${enrollment.course.id}`;
  };

  const handleUnenrollConfirm = async () => {
    if (!selectedEnrollment) return;

    try {
      setUnenrolling(true);
      const { enrollmentApi } = await import('@/lib/api');
      const response = await enrollmentApi.unenroll(selectedEnrollment.id);

      if (response.success) {
        // Refresh dashboard data
        const userStr = localStorage.getItem('user');
        if (userStr) {
          const user = JSON.parse(userStr);
          const refreshResponse = await dashboardApi.getStudentDashboard(user.id);
          if (refreshResponse.success && refreshResponse.data) {
            const data = refreshResponse.data as any;
            
            // Map API response to component format (same as in useEffect)
            const mappedCourses = data.courses.map((item: any) => ({
              id: item.enrollment_id,
              user_id: user.id,
              course_id: item.course.id,
              enrolled_at: item.enrolled_at,
              progress: item.progress_percentage,
              status: item.status,
              course: item.course
            }));
            
            const transformedData: DashboardData = {
              user: user,
              enrolled_courses: {
                in_progress: mappedCourses.filter((c: any) => c.status === 'active'),
                completed: mappedCourses.filter((c: any) => c.status === 'completed')
              },
              stats: {
                total_enrolled: data.total || 0,
                in_progress: mappedCourses.filter((c: any) => c.status === 'active').length,
                completed: mappedCourses.filter((c: any) => c.status === 'completed').length
              }
            };
            setDashboardData(transformedData);
          }
        }
        setShowUnenrollModal(false);
        setSelectedEnrollment(null);
      } else {
        alert(response.error || 'Failed to unenroll from course');
      }
    } catch (err) {
      console.error('Error unenrolling:', err);
      alert('Failed to unenroll from course');
    } finally {
      setUnenrolling(false);
    }
  };

  const handleTogglePublish = async (course: CourseData) => {
    const newStatus = course.status === 'active' ? 'unpublished' : 'active';
    
    try {
      const response = await fetch(`http://localhost:5001/api/courses/${course.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': dashboardData?.user?.id?.toString() || '',
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        window.location.reload();
      }
    } catch (error) {
      console.error('Error toggling publish status:', error);
    }
  };

  const handleDeleteCourse = async () => {
    if (!selectedCourse) return;

    setDeletingCourse(true);
    try {
      const response = await fetch(`http://localhost:5001/api/courses/${selectedCourse.id}`, {
        method: 'DELETE',
        headers: {
          'X-User-Id': dashboardData?.user?.id?.toString() || '',
        },
      });

      if (response.ok) {
        window.location.reload();
      }
    } catch (error) {
      console.error('Error deleting course:', error);
    }

    setDeletingCourse(false);
    setShowDeleteCourseModal(false);
    setSelectedCourse(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {error || 'Dashboard not available'}
          </h2>
          <Link href="/" className="text-blue-600 hover:underline">Return to home</Link>
        </div>
      </div>
    );
  }

  const isInstructor = dashboardData.user.role === 'instructor';
  const isAdmin = dashboardData.user.role === 'admin';
  
  console.log('Dashboard data:', dashboardData);
  console.log('User role:', dashboardData.user.role);
  console.log('Is Admin:', isAdmin);
  console.log('Users array:', users);

  return (
    <main className="min-h-screen bg-gray-50">
      <Header />

      {showUnenrollModal && selectedEnrollment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 shadow-2xl">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                <svg className="h-10 w-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Unenroll from Course?</h3>
              <p className="text-gray-600 mb-2">Are you sure you want to unenroll from:</p>
              <p className="text-lg font-semibold text-gray-900 mb-2">{selectedEnrollment.course.title}</p>
              <p className="text-sm text-gray-500 mb-6">Your progress ({selectedEnrollment.progress}%) will be lost.</p>
              <div className="flex flex-col gap-3">
                <button
                  onClick={handleUnenrollConfirm}
                  disabled={unenrolling}
                  className="w-full bg-red-600 text-white py-3 rounded-lg font-bold hover:bg-red-700 disabled:bg-gray-400"
                >
                  {unenrolling ? 'Unenrolling...' : 'Yes, Unenroll'}
                </button>
                <button
                  onClick={() => {
                    setShowUnenrollModal(false);
                    setSelectedEnrollment(null);
                  }}
                  disabled={unenrolling}
                  className="w-full border-2 border-gray-300 text-gray-900 py-3 rounded-lg font-bold hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}


      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-12 flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome back, {dashboardData.user.name}!
            </h2>
            <p className="text-gray-600">
              {isAdmin ? 'Manage platform users and content' : isInstructor ? 'Manage your courses and students' : 'Continue your learning journey'}
            </p>
          </div>
          {isInstructor && (
            <Link href="/instructor/courses/new">
              <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700">
                + Create New Course
              </button>
            </Link>
          )}
        </div>

        {/* Admin Dashboard */}
        {isAdmin && (
          <>
            {/* Admin Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Students</p>
                    <p className="text-3xl font-bold text-gray-900">{dashboardData.stats.total_students || 0}</p>
                  </div>
                  <div className="bg-blue-100 p-3 rounded-lg">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Instructors</p>
                    <p className="text-3xl font-bold text-gray-900">{dashboardData.stats.total_lecturers || 0}</p>
                  </div>
                  <div className="bg-purple-100 p-3 rounded-lg">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Courses</p>
                    <p className="text-3xl font-bold text-gray-900">{dashboardData.stats.total_courses || 0}</p>
                  </div>
                  <div className="bg-green-100 p-3 rounded-lg">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Enrollments</p>
                    <p className="text-3xl font-bold text-gray-900">{dashboardData.stats.total_enrollments || 0}</p>
                  </div>
                  <div className="bg-yellow-100 p-3 rounded-lg">
                    <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Users Management */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-xl font-bold text-gray-900">User Management</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setUserFilter('active')}
                      className={`px-4 py-2 rounded-md font-medium ${userFilter === 'active' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                    >
                      Active
                    </button>
                    <button
                      onClick={() => setUserFilter('deleted')}
                      className={`px-4 py-2 rounded-md font-medium ${userFilter === 'deleted' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                    >
                      Deleted
                    </button>
                    <button
                      onClick={() => setUserFilter('all')}
                      className={`px-4 py-2 rounded-md font-medium ${userFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                    >
                      All
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {users.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            user.role === 'admin' ? 'bg-red-100 text-red-800' :
                            user.role === 'instructor' ? 'bg-purple-100 text-purple-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {user.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(user.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {user.role !== 'admin' && (
                            <button
                              onClick={() => {
                                setSelectedUser(user);
                                setShowDeleteUserModal(true);
                              }}
                              className="text-red-600 hover:text-red-900 font-medium"
                            >
                              Delete
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {users.length === 0 && (
                  <div className="text-center py-12 text-gray-500">No users found</div>
                )}
              </div>
            </div>
          </>
        )}

        {!isInstructor && !isAdmin && (
          <>
            <div className="flex gap-8 mb-8 border-b border-gray-200">
              <button
                onClick={() => setActiveTab('inprogress')}
                className={`px-4 py-3 border-b-2 font-medium ${activeTab === 'inprogress'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
              >
                In Progress ({dashboardData.stats.in_progress || 0})
              </button>
              <button
                onClick={() => setActiveTab('completed')}
                className={`px-4 py-3 border-b-2 font-medium ${activeTab === 'completed'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
              >
                Completed ({dashboardData.stats.completed || 0})
              </button>
            </div>

            <div className="mb-16">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">
                {activeTab === 'inprogress' ? 'Continuing Education' : 'Completed Courses'}
              </h3>

              {activeTab === 'inprogress' && (
                <div className="grid md:grid-cols-3 gap-6">
                  {dashboardData.enrolled_courses?.in_progress && dashboardData.enrolled_courses.in_progress.length > 0 ? (
                    dashboardData.enrolled_courses.in_progress.map((enrollment) => (
                      <div key={enrollment.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden">
                        <Link href={`/course/${enrollment.course.id}`}>
                          <div className="cursor-pointer group">
                            <div className="relative">
                              <Image
                                src={getValidImageUrl(enrollment.course.image)}
                                alt={enrollment.course.title}
                                width={400}
                                height={160}
                                className="w-full h-40 object-cover"
                              />
                            </div>
                            <div className="p-5">
                              <h4 className="text-lg font-bold text-gray-900 mb-1">{enrollment.course.title}</h4>
                              <p className="text-sm text-gray-600 mb-4">{enrollment.course.instructor || enrollment.course.company}</p>

                              <div className="mb-3">
                                <div className="flex justify-between items-center mb-2">
                                  <span className="text-xs font-medium text-gray-600">Progress</span>
                                  <span className="text-xs font-bold text-gray-900">{enrollment.progress}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div
                                    className="bg-blue-600 h-2 rounded-full transition-all"
                                    style={{ width: `${enrollment.progress}%` }}
                                  />
                                </div>
                              </div>
                            </div>
                          </div>
                        </Link>
                        <div className="px-5 pb-5 space-y-2">
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              handleContinueLearning(enrollment);
                            }}
                            className="w-full bg-blue-600 text-white py-2 rounded-md font-medium hover:bg-blue-700 transition"
                          >
                            Continue Learning
                          </button>
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              handleUnenrollClick(enrollment);
                            }}
                            className="w-full border-2 border-red-300 text-red-600 py-2 rounded-md font-medium hover:bg-red-50 transition"
                          >
                            Unenroll
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-3 text-center py-12">
                      <p className="text-gray-600 mb-4">You haven&apos;t enrolled in any courses yet</p>
                      <Link href="/" className="text-blue-600 hover:underline">Explore courses</Link>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'completed' && (
                <div className="grid md:grid-cols-3 gap-6">
                  {dashboardData.enrolled_courses?.completed && dashboardData.enrolled_courses.completed.length > 0 ? (
                    dashboardData.enrolled_courses.completed.map((enrollment) => (
                      <Link key={enrollment.id} href={`/course/${enrollment.course.id}`}>
                        <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden cursor-pointer group">
                          <div className="relative">
                            <Image
                              src={getValidImageUrl(enrollment.course.image)}
                              alt={enrollment.course.title}
                              width={400}
                              height={160}
                              className="w-full h-40 object-cover"
                            />
                            <div className="absolute top-3 right-3 bg-green-600 text-white px-3 py-1 rounded-full text-xs font-bold">
                              Completed
                            </div>
                          </div>
                          <div className="p-5">
                            <h4 className="text-lg font-bold text-gray-900 mb-1">{enrollment.course.title}</h4>
                            <p className="text-sm text-gray-600 mb-4">{enrollment.course.instructor || enrollment.course.company}</p>

                            <button className="w-full border-2 border-blue-600 text-blue-600 py-2 rounded-md font-medium hover:bg-blue-50 transition">
                              View Certificate
                            </button>
                          </div>
                        </div>
                      </Link>
                    ))
                  ) : (
                    <div className="col-span-3 text-center py-12">
                      <p className="text-gray-600">No completed courses yet</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}

        {isInstructor && (
          <>
            <div className="flex gap-8 mb-8 border-b border-gray-200">
              <button
                onClick={() => setActiveTab('published')}
                className={`px-4 py-3 border-b-2 font-medium ${activeTab === 'published'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
              >
                Published ({dashboardData.stats.published || 0})
              </button>
              <button
                onClick={() => setActiveTab('drafts')}
                className={`px-4 py-3 border-b-2 font-medium ${activeTab === 'drafts'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
              >
                Drafts ({dashboardData.stats.drafts || 0})
              </button>
            </div>

            <div className="mb-16">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold text-gray-900">
                  {activeTab === 'published' ? 'Published Courses' : 'Draft Courses'}
                </h3>

              </div>

              {activeTab === 'published' && (
                <div className="grid md:grid-cols-3 gap-6">
                  {dashboardData.created_courses?.published && dashboardData.created_courses.published.length > 0 ? (
                    dashboardData.created_courses.published.map((course) => (
                      <div key={course.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden">
                        <Link href={`/course/${course.id}`}>
                          <div className="cursor-pointer group">
                            <div className="relative">
                              <Image
                                src={getValidImageUrl(course.image)}
                                alt={course.title}
                                width={400}
                                height={160}
                                className="w-full h-40 object-cover"
                              />
                            </div>
                            <div className="p-5">
                              <h4 className="text-lg font-bold text-gray-900 mb-1">{course.title}</h4>
                              <p className="text-sm text-gray-600 mb-4">{course.level} • {course.duration}</p>

                              <div className="grid grid-cols-2 gap-4 mb-3">
                                <div>
                                  <p className="text-xs text-gray-600">Students</p>
                                  <p className="text-sm font-bold text-gray-900">{course.students?.toLocaleString() || 0}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-gray-600">Rating</p>
                                  <p className="text-sm font-bold text-gray-900">{course.rating || 'N/A'}</p>
                                </div>
                              </div>
                            </div>
                          </div>
                        </Link>
                        <div className="px-5 pb-5 space-y-2">
                          <Link href={`/instructor/courses/${course.id}/edit`}>
                            <button className="w-full bg-blue-600 text-white py-2 rounded-md font-medium hover:bg-blue-700 transition">
                              Edit Course
                            </button>
                          </Link>
                          <button
                            onClick={() => handleTogglePublish(course)}
                            className="w-full bg-yellow-600 text-white py-2 rounded-md font-medium hover:bg-yellow-700 transition"
                          >
                            Unpublish
                          </button>
                          <button
                            onClick={() => {
                              setSelectedCourse(course);
                              setShowDeleteCourseModal(true);
                            }}
                            className="w-full border-2 border-red-300 text-red-600 py-2 rounded-md font-medium hover:bg-red-50 transition"
                          >
                            Delete Course
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-3 text-center py-12">
                      <p className="text-gray-600 mb-4">You haven&apos;t published any courses yet</p>
                      <Link href="/instructor/courses/new">
                        <button className="text-blue-600 hover:underline font-semibold">Create your first course</button>
                      </Link>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'drafts' && (
                <div className="grid md:grid-cols-3 gap-6">
                  {dashboardData.created_courses?.drafts && dashboardData.created_courses.drafts.length > 0 ? (
                    dashboardData.created_courses.drafts.map((course) => (
                      <div key={course.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden cursor-pointer group">
                        <div className="relative">
                          <Image
                            src={getValidImageUrl(course.image)}
                            alt={course.title}
                            width={400}
                            height={160}
                            className="w-full h-40 object-cover"
                          />
                          <div className="absolute top-3 right-3 bg-yellow-500 text-white px-3 py-1 rounded-full text-xs font-bold">
                            Draft
                          </div>
                        </div>
                        <div className="p-5">
                          <h4 className="text-lg font-bold text-gray-900 mb-1">{course.title}</h4>
                          <p className="text-sm text-gray-600 mb-4">{course.level} • {course.duration}</p>

                          <div className="space-y-2">
                            <Link href={`/instructor/courses/${course.id}/edit`}>
                              <button className="w-full bg-blue-600 text-white py-2 rounded-md font-medium hover:bg-blue-700 transition">
                                Continue Editing
                              </button>
                            </Link>
                            <button
                              onClick={() => handleTogglePublish(course)}
                              className="w-full bg-green-600 text-white py-2 rounded-md font-medium hover:bg-green-700 transition"
                            >
                              Publish Course
                            </button>
                            <button
                              onClick={() => {
                                setSelectedCourse(course);
                                setShowDeleteCourseModal(true);
                              }}
                              className="w-full border-2 border-red-300 text-red-600 py-2 rounded-md font-medium hover:bg-red-50 transition"
                            >
                              Delete Course
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-3 text-center py-12">
                      <p className="text-gray-600">No draft courses</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}

        {isInstructor && (
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-gray-600 font-medium">Total Students</h4>
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <p className="text-3xl font-bold text-gray-900">{dashboardData.stats.total_students?.toLocaleString() || 0}</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-gray-600 font-medium">Total Courses</h4>
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <p className="text-3xl font-bold text-gray-900">{dashboardData.stats.total_courses || 0}</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-gray-600 font-medium">Total Reviews</h4>
                <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </div>
              <p className="text-3xl font-bold text-gray-900">{dashboardData.stats.total_reviews?.toLocaleString() || 0}</p>
            </div>
          </div>
        )}
      </div>

      {/* Delete Course Confirmation Modal */}
      {showDeleteCourseModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Delete Course</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete &quot;{selectedCourse?.title}&quot;? This action cannot be undone.
              All course content, lectures, and student progress will be permanently deleted.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDeleteCourseModal(false);
                  setSelectedCourse(null);
                }}
                disabled={deletingCourse}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteCourse}
                disabled={deletingCourse}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md font-medium hover:bg-red-700 disabled:opacity-50"
              >
                {deletingCourse ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete User Modal (Admin) */}
      {showDeleteUserModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Delete User</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete <strong>{selectedUser.name}</strong>? This action will set their status to deleted.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowDeleteUserModal(false);
                  setSelectedUser(null);
                }}
                disabled={deletingUser}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteUser}
                disabled={deletingUser}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
              >
                {deletingUser ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
