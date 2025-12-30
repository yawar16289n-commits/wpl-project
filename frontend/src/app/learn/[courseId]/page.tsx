'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Header from '@/app/components/Header';
import { courseApi, lectureApi, lectureResourceApi, enrollmentApi } from '@/lib/api';

export default function LearnCoursePage() {
    const params = useParams();
    const router = useRouter();
    const courseId = params.courseId as string;

    const [course, setCourse] = useState<any>(null);
    const [lectures, setLectures] = useState<any[]>([]);
    const [enrollment, setEnrollment] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            router.push('/');
            return;
        }
        setUser(JSON.parse(userData));
        fetchCourseData(JSON.parse(userData));
    }, [courseId]);

    const fetchCourseData = async (userData: any) => {
        try {
            setLoading(true);

            // Fetch course
            const courseRes = await courseApi.getCourse(Number(courseId));
            if (courseRes.success && courseRes.data) {
                setCourse((courseRes.data as any).course);
            }

            // Fetch lectures
            const lecturesRes = await lectureApi.getCourseLectures(Number(courseId));
            if (lecturesRes.success && lecturesRes.data) {
                const lecturesData = (lecturesRes.data as any).lectures || [];
                setLectures(lecturesData);

                // Redirect to first lesson if available
                if (lecturesData.length > 0) {
                    const firstLecture = lecturesData[0];
                    const lessonsRes = await lectureResourceApi.getLectureResources(firstLecture.id);
                    if (lessonsRes.success && lessonsRes.data) {
                        const lessons = (lessonsRes.data as any).resources || [];
                        if (lessons.length > 0) {
                            router.push(`/learn/${courseId}/${firstLecture.id}/${lessons[0].id}`);
                        }
                    }
                }
            }

            // Check enrollment
            const enrollmentRes = await enrollmentApi.checkEnrollment(userData.id, Number(courseId));
            if (enrollmentRes.success && enrollmentRes.data) {
                if (!(enrollmentRes.data as any).enrolled) {
                    router.push(`/course/${courseId}`);
                } else {
                    setEnrollment((enrollmentRes.data as any).enrollment);
                }
            }
        } catch (err) {
            console.error('Failed to load course', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <main className="min-h-screen bg-gray-50">
                <Header />
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-gray-50">
            <Header />

            <div className="max-w-6xl mx-auto px-4 py-8">
                <div className="text-center">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">{course?.title}</h1>
                    <p className="text-gray-600 mb-6">Loading course content...</p>
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                </div>
            </div>
        </main>
    );
}
