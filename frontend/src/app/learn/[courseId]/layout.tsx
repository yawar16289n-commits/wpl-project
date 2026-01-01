'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { courseApi, lectureApi } from '@/lib/api';
import CourseSidebar from './_components/CourseSidebar';
import TopNavigation from './_components/TopNavigation';

export default function LearnLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const params = useParams();
    const router = useRouter();
    const courseId = Number(params.courseId);

    const [course, setCourse] = useState<any>(null);
    const [modules, setModules] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCourseData = async () => {
            try {
                setLoading(true);
                const userStr = localStorage.getItem('user');
                if (!userStr) {
                    router.push('/');
                    return;
                }

                const courseRes = await courseApi.getCourse(courseId);
                if (courseRes.success && courseRes.data) {
                    setCourse((courseRes.data as any).course);
                }

                const lecturesRes = await lectureApi.getCourseLectures(courseId);
                if (lecturesRes.success && lecturesRes.data) {
                    setModules((lecturesRes.data as any).lectures || []);
                }
            } catch (err) {
                console.error('Failed to load course data', err);
            } finally {
                setLoading(false);
            }
        };

        if (courseId) {
            fetchCourseData();
        }
    }, [courseId]);

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!course) {
        return null;
    }

    return (
        <div className="flex h-screen bg-gray-50 overflow-hidden">
            <CourseSidebar courseId={courseId} modules={modules} />

            <div className="flex-1 flex flex-col min-w-0">
                <TopNavigation courseId={courseId} courseTitle={course.title} />

                <main className="flex-1 overflow-y-auto p-8">
                    {children}
                </main>
            </div>
        </div>
    );
}
