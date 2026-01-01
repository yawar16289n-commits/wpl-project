'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { lectureResourceApi, lectureApi, progressApi, enrollmentApi } from '@/lib/api';

export default function LessonPage() {
    const params = useParams();
    const courseId = params.courseId as string;
    const lectureId = params.lectureId as string;
    const lessonId = params.lessonId as string;

    const [lesson, setLesson] = useState<any>(null);
    const [lecture, setLecture] = useState<any>(null);
    const [enrollment, setEnrollment] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [isCompleted, setIsCompleted] = useState(false);
    const [user, setUser] = useState<any>(null);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (userData) {
            setUser(JSON.parse(userData));
        }

        fetchLessonData();
    }, [lessonId]);

    const fetchLessonData = async () => {
        try {
            setLoading(true);

            // Fetch lesson
            const lessonRes = await lectureResourceApi.getResource(Number(lessonId));
            if (lessonRes.success && lessonRes.data) {
                setLesson((lessonRes.data as any).resource);
            }

            // Fetch lecture
            const lectureRes = await lectureApi.getLecture(Number(lectureId));
            if (lectureRes.success && lectureRes.data) {
                setLecture((lectureRes.data as any).lecture);
            }

            // Check if lesson is completed
            const userData = localStorage.getItem('user');
            if (userData) {
                const userId = JSON.parse(userData).id;
                
                // Fetch enrollment
                const enrollmentRes = await enrollmentApi.checkEnrollment(userId, Number(courseId));
                if (enrollmentRes.success && enrollmentRes.data) {
                    const enrollmentData = (enrollmentRes.data as any).enrollment;
                    setEnrollment(enrollmentData);
                    
                    // Check completed lectures using new API
                    if (enrollmentData) {
                        const completedRes = await progressApi.getCompletedLectures(enrollmentData.id);
                        if (completedRes.success && completedRes.data) {
                            const completedLectures = (completedRes.data as any).completed_lectures || [];
                            const isLessonCompleted = completedLectures.some(
                                (l: any) => l.lecture_resource_id === Number(lessonId)
                            );
                            setIsCompleted(isLessonCompleted);
                        }
                    }
                }
            }
        } catch (err) {
            setError('Failed to load lesson');
        } finally {
            setLoading(false);
        }
    };

    const handleToggleCompletion = async () => {
        if (!user) {
            setError('Please log in to update lesson status');
            return;
        }

        if (!enrollment) {
            setError('Enrollment not found');
            return;
        }

        try {
            const response = await progressApi.toggleLectureCompletion(
                enrollment.id,
                Number(lessonId)
            );

            if (response.success && response.data) {
                const data = response.data as any;
                setIsCompleted(!isCompleted);
                const message = data.progress?.completed 
                    ? 'Lesson marked as complete! 🎉' 
                    : 'Lesson marked as incomplete';
                setSuccessMessage(message);
                setTimeout(() => setSuccessMessage(''), 3000);
            } else {
                setError(response.error || 'Failed to update lesson status');
            }
        } catch (err) {
            console.error('Toggle completion error:', err);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto">
            {/* Messages */}
            {error && (
                <div className="mb-4 p-4 bg-red-100 text-red-800 rounded-lg">
                    {error}
                </div>
            )}
            {successMessage && (
                <div className="mb-4 p-4 bg-green-100 text-green-800 rounded-lg">
                    {successMessage}
                </div>
            )}

            {/* Lesson Content */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-6">
                <div className="flex items-center gap-3 mb-6">
                    <span className="text-4xl bg-gray-100 p-3 rounded-lg">
                        {lesson?.resource_type === 'video' ? '🎥' : '📝'}
                    </span>
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">{lesson?.title}</h1>
                        <p className="text-gray-500">{lecture?.title}</p>
                    </div>
                </div>

                {lesson?.duration && (
                    <div className="mb-6 text-gray-600 flex items-center gap-2">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="font-medium">Duration:</span> {lesson.duration}
                    </div>
                )}

                {/* Video Lesson */}
                {lesson?.resource_type === 'video' && lesson?.url && (
                    <div className="mb-8">
                        <div className="aspect-video bg-black rounded-xl overflow-hidden shadow-lg">
                            {lesson.url.includes('youtube.com') || lesson.url.includes('youtu.be') ? (
                                <iframe
                                    className="w-full h-full"
                                    src={lesson.url.replace('watch?v=', 'embed/')}
                                    title={lesson.title}
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowFullScreen
                                ></iframe>
                            ) : lesson.url.includes('vimeo.com') ? (
                                <iframe
                                    className="w-full h-full"
                                    src={lesson.url.replace('vimeo.com/', 'player.vimeo.com/video/')}
                                    title={lesson.title}
                                    allow="autoplay; fullscreen; picture-in-picture"
                                    allowFullScreen
                                ></iframe>
                            ) : (
                                <video className="w-full h-full" controls>
                                    <source src={lesson.url} />
                                    Your browser does not support the video tag.
                                </video>
                            )}
                        </div>
                    </div>
                )}

                {/* Text Lesson */}
                {lesson?.resource_type === 'text' && lesson?.content && (
                    <div className="prose prose-lg max-w-none mb-8">
                        <div className="bg-gray-50 rounded-xl p-8 whitespace-pre-wrap font-serif leading-relaxed text-gray-800">
                            {lesson.content}
                        </div>
                    </div>
                )}

                {/* Toggle Completion Button */}
                <div className="flex justify-end pt-6 border-t border-gray-100">
                    {isCompleted ? (
                        <button
                            onClick={handleToggleCompletion}
                            className="flex items-center gap-2 px-8 py-3 rounded-lg font-bold text-lg transition-all shadow-sm bg-green-100 text-green-700 border border-green-200 hover:bg-gray-100 hover:text-gray-700"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            Completed
                        </button>
                    ) : (
                        <button
                            onClick={handleToggleCompletion}
                            className="flex items-center gap-2 px-8 py-3 rounded-lg font-bold text-lg transition-all shadow-sm bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md"
                        >
                            Mark as Completed
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
