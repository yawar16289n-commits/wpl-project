'use client';

import Link from 'next/link';

interface TopNavigationProps {
    courseId: number;
    courseTitle: string;
}

export default function TopNavigation({ courseId, courseTitle }: TopNavigationProps) {
    return (
        <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center shadow-sm z-10">
            <Link
                href={`/course/${courseId}`}
                className="flex items-center gap-3 text-gray-700 hover:text-blue-600 transition-colors group"
            >
                <div className="p-2 rounded-full group-hover:bg-blue-50 transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                </div>
                <h1 className="font-bold text-lg truncate">
                    {courseTitle}
                </h1>
            </Link>
        </div>
    );
}
