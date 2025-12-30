'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '@/app/components/Header';
import ReviewsRatings from '@/app/components/ReviewsRatings';
import { courseApi, enrollmentApi } from '@/lib/api';

export default function CourseDetail() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.id as string;
  const [activeTab, setActiveTab] = useState('overview');
  const [course, setCourse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [enrollmentId, setEnrollmentId] = useState<number | null>(null);
  const [enrolling, setEnrolling] = useState(false);
  const [enrollmentMessage, setEnrollmentMessage] = useState<string | null>(null);
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    const fetchCourseAndEnrollment = async () => {
      try {
        setLoading(true);
        const response = await courseApi.getCourse(Number(courseId));
        
        if (response.success && response.data) {
          const courseData = (response.data as { course: any }).course;
          setCourse(courseData);

          const userStr = localStorage.getItem('user');
          if (userStr) {
            const user = JSON.parse(userStr);
            setUserId(user.id);
            const enrollmentCheck = await enrollmentApi.checkEnrollment(user.id, Number(courseId));
            
            if (enrollmentCheck.success && enrollmentCheck.data) {
              const enrollmentData = enrollmentCheck.data as { enrolled: boolean; enrollment_id?: number };
              setIsEnrolled(enrollmentData.enrolled);
              if (enrollmentData.enrollment_id) {
                setEnrollmentId(enrollmentData.enrollment_id);
              }
            }
          }
        } else {
          setError(response.error || 'Failed to load course');
        }
      } catch (err) {
        console.error('Error fetching course:', err);
        setError('Failed to load course');
      } finally {
        setLoading(false);
      }
    };

    fetchCourseAndEnrollment();
  }, [courseId]);

  const handleEnroll = async () => {
    try {
      setEnrolling(true);
      setEnrollmentMessage(null);

      const userStr = localStorage.getItem('user');
      if (!userStr) {
        setEnrollmentMessage('Please log in to enroll in this course');
        return;
      }

      const user = JSON.parse(userStr);
      const response = await enrollmentApi.enroll(user.id, Number(courseId));

      if (response.success) {
        setIsEnrolled(true);
        setShowEnrollModal(true);
      } else {
        setEnrollmentMessage(response.error || 'Failed to enroll in course');
      }
    } catch (err) {
      console.error('Error enrolling:', err);
      setEnrollmentMessage('Failed to enroll in course');
    } finally {
      setEnrolling(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {error || 'Course not found'}
          </h2>
          <Link href="/dashboard" className="text-blue-600 hover:underline">Return to dashboard</Link>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-white">
      {showEnrollModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 shadow-2xl">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
                <svg className="h-10 w-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Successfully Enrolled!</h3>
              <p className="text-gray-600 mb-2">You&apos;ve been enrolled in:</p>
              <p className="text-lg font-semibold text-gray-900 mb-6">{course?.title}</p>
              <div className="flex flex-col gap-3">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700"
                >
                  Go to Dashboard
                </button>
                <button
                  onClick={() => setShowEnrollModal(false)}
                  className="w-full border-2 border-gray-300 text-gray-900 py-3 rounded-lg font-bold hover:bg-gray-50"
                >
                  Continue Browsing
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <Header />

      <section className="bg-blue-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2">
            <div className="flex gap-3 mb-4">
              <span className="inline-block px-3 py-1 bg-blue-800 rounded-full text-sm font-medium">
                {course.level}
              </span>
              <span className="inline-block px-3 py-1 bg-blue-800 rounded-full text-sm font-medium">
                {course.duration}
              </span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">{course.title}</h1>
            <p className="text-lg text-blue-100 mb-6">{course.description}</p>
            
            <div className="flex items-center gap-6 mb-6">
              <div className="flex items-center gap-2">
                <div className="flex gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className="w-5 h-5 text-yellow-400 fill-current" viewBox="0 0 24 24">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                    </svg>
                  ))}
                </div>
                <span className="font-semibold">{course.rating}</span>
                <span className="text-gray-300">({course.reviews?.toLocaleString() || 0} reviews)</span>
              </div>
              <div className="text-gray-300">
                {course.students?.toLocaleString() || 0} students
              </div>
            </div>

            <div className="flex items-center gap-3">
              {course.instructor_image && (
                <Image src={course.instructor_image} alt={course.instructor || 'Instructor'} width={48} height={48} className="w-12 h-12 rounded-full object-cover" />
              )}
              <div>
                <p className="font-semibold">Instructor: {course.instructor}</p>
                <p className="text-blue-200 text-sm">{course.company}</p>
              </div>
            </div>
          </div>

          <div className="bg-white text-gray-900 rounded-lg p-6 h-fit">
            {course.image && (
              <Image src={course.image} alt={course.title} width={400} height={160} className="w-full h-40 object-cover rounded-lg mb-4" />
            )}
            
            <div className="space-y-4">
              {enrollmentMessage && (
                <div className={`p-3 rounded-lg text-sm font-medium ${
                  enrollmentMessage.includes('Success') || enrollmentMessage.includes('enrolled')
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {enrollmentMessage}
                </div>
              )}

              {isEnrolled ? (
                <Link href="/dashboard">
                  <button className="w-full bg-green-600 text-white py-3 rounded-lg font-bold hover:bg-green-700 flex items-center justify-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Enrolled - Go to Dashboard
                  </button>
                </Link>
              ) : (
                <button 
                  onClick={handleEnroll}
                  disabled={enrolling}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {enrolling ? 'Enrolling...' : 'Enroll Now'}
                </button>
              )}

              <div className="space-y-2 text-sm text-gray-600 pt-4 border-t border-gray-200">
                <p>✓ Access on mobile and desktop</p>
                <p>✓ 30-day money-back guarantee</p>
                <p>✓ {course.level} level</p>
                <p>✓ {course.duration}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-8">
            {['Overview', 'Curriculum', 'Reviews', 'About Instructor'].map((tab) => (
              <button
                key={tab.toLowerCase()}
                onClick={() => setActiveTab(tab.toLowerCase().replace(' ', ''))}
                className={`py-4 border-b-2 font-medium transition ${
                  activeTab === tab.toLowerCase().replace(' ', '')
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="py-12">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2">
            {activeTab === 'overview' && (
              <div className="space-y-8">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">About this course</h2>
                  <p className="text-gray-700 leading-relaxed">{course.about}</p>
                </div>

                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">What you&apos;ll learn</h2>
                  <div className="grid md:grid-cols-2 gap-4">
                    {(course.learningOutcomes || course.learning_outcomes || []).map((outcome: string, i: number) => (
                      <div key={i} className="flex gap-3">
                        <svg className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
                        </svg>
                        <p className="text-gray-700">{outcome}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Skills you&apos;ll gain</h2>
                  <div className="flex flex-wrap gap-3">
                    {(course.skills || []).map((skill: string, i: number) => (
                      <span key={i} className="px-4 py-2 bg-gray-200 text-gray-900 rounded-full font-medium">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'curriculum' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Curriculum</h2>
                {(course.courses || []).map((module: any, i: number) => (
                  <div key={i} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">
                          Course {module.number}: {module.title}
                        </h3>
                        <p className="text-gray-600 mt-1">
                          {module.lessons} lessons • {module.duration}
                        </p>
                      </div>
                      <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7"/>
                      </svg>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'reviews' && (
              <ReviewsRatings 
                courseId={Number(courseId)} 
                userId={userId} 
                isEnrolled={isEnrolled} 
              />
            )}

            {activeTab === 'aboutinstructor' && (
              <div className="space-y-6">
                <div className="flex gap-6">
                  {course.instructor_image && (
                    <Image src={course.instructor_image} alt={course.instructor || 'Instructor'} 
                      width={96} height={96} className="w-24 h-24 rounded-full object-cover" />
                  )}
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{course.instructor}</h2>
                    <p className="text-gray-600">{course.company}</p>
                  </div>
                </div>
                <p className="text-gray-700 leading-relaxed">
                  {course.instructor_bio}
                </p>
              </div>
            )}
          </div>

          <div className="space-y-6">
            <div className="border border-gray-200 rounded-lg p-6">
              <h3 className="font-bold text-gray-900 mb-4">Course Details</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-gray-600">Level</p>
                  <p className="font-medium text-gray-900">{course.level}</p>
                </div>
                <div>
                  <p className="text-gray-600">Duration</p>
                  <p className="font-medium text-gray-900">{course.duration}</p>
                </div>
                <div>
                  <p className="text-gray-600">Language</p>
                  <p className="font-medium text-gray-900">{course.language}</p>
                </div>
                {course.subtitles && course.subtitles.length > 0 && (
                  <div>
                    <p className="text-gray-600">Subtitles</p>
                    <p className="font-medium text-gray-900">{course.subtitles.join(', ')}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="border border-gray-200 rounded-lg p-6">
              <h3 className="font-bold text-gray-900 mb-4">Share</h3>
              <div className="space-y-2">
                <button className="w-full flex items-center gap-2 p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                  <span className="text-gray-900 font-medium">Facebook</span>
                </button>
                <button className="w-full flex items-center gap-2 p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2s9 5 20 5a9.5 9.5 0 00-9-5.5c4.75 2.25 7-7 7-7a10.6 10.6 0 01-9 5c3 1.5 7 1.5 9 0"/>
                  </svg>
                  <span className="text-gray-900 font-medium">Twitter</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
