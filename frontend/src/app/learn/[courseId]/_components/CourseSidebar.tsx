'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, usePathname } from 'next/navigation';
import { lectureResourceApi } from '@/lib/api';

interface CourseSidebarProps {
    courseId: number;
    modules: any[];
}

export default function CourseSidebar({ courseId, modules }: CourseSidebarProps) {
    const params = useParams();
    const pathname = usePathname();
    const currentLessonId = params.lessonId ? Number(params.lessonId) : null;
    const currentLectureId = params.lectureId ? Number(params.lectureId) : null;

    const [expandedModules, setExpandedModules] = useState<Set<number>>(new Set());
    const [moduleLessons, setModuleLessons] = useState<Record<number, any[]>>({});
    const [loading, setLoading] = useState<Record<number, boolean>>({});

    // Auto-expand the current module
    useEffect(() => {
        if (currentLectureId) {
            setExpandedModules(prev => {
                const newSet = new Set(prev);
                newSet.add(currentLectureId);
                return newSet;
            });
            fetchLessons(currentLectureId);
        }
    }, [currentLectureId]);

    const fetchLessons = async (moduleId: number) => {
        if (moduleLessons[moduleId] || loading[moduleId]) return;

        setLoading(prev => ({ ...prev, [moduleId]: true }));
        try {
            const response = await lectureResourceApi.getLectureResources(moduleId);
            if (response.success && response.data) {
                setModuleLessons(prev => ({
                    ...prev,
                    [moduleId]: (response.data as any).resources || []
                }));
            }
        } catch (err) {
            console.error('Failed to load lessons', err);
        } finally {
            setLoading(prev => ({ ...prev, [moduleId]: false }));
        }
    };

    const toggleModule = (moduleId: number) => {
        setExpandedModules(prev => {
            const newSet = new Set(prev);
            if (newSet.has(moduleId)) {
                newSet.delete(moduleId);
            } else {
                newSet.add(moduleId);
                fetchLessons(moduleId);
            }
            return newSet;
        });
    };

    return (
        <div className="w-80 h-screen bg-white border-r border-gray-200 flex flex-col flex-shrink-0">
            <div className="p-4 border-b border-gray-200">
                <h2 className="font-bold text-gray-900">Course Content</h2>
            </div>

            <div className="flex-1 overflow-y-auto">
                {modules.map((module) => {
                    const isExpanded = expandedModules.has(module.id);
                    const lessons = moduleLessons[module.id] || [];
                    const isLoading = loading[module.id];

                    return (
                        <div key={module.id} className="border-b border-gray-100">
                            <button
                                onClick={() => toggleModule(module.id)}
                                className="w-full px-4 py-3 flex items-start justify-between hover:bg-gray-50 text-left transition-colors"
                            >
                                <div className="flex-1">
                                    <h3 className="font-medium text-gray-900 text-sm">
                                        {module.number}. {module.title}
                                    </h3>
                                    <p className="text-xs text-gray-500 mt-1">
                                        {module.lessons} lessons • {module.duration}
                                    </p>
                                </div>
                                <svg
                                    className={`w-4 h-4 text-gray-400 mt-1 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                            </button>

                            {isExpanded && (
                                <div className="bg-gray-50">
                                    {isLoading ? (
                                        <div className="p-4 text-center">
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mx-auto"></div>
                                        </div>
                                    ) : lessons.length > 0 ? (
                                        <div className="py-2">
                                            {lessons.map((lesson) => {
                                                const isActive = lesson.id === currentLessonId;
                                                return (
                                                    <Link
                                                        key={lesson.id}
                                                        href={`/learn/${courseId}/${module.id}/${lesson.id}`}
                                                        className={`block px-4 py-2 text-sm flex items-center gap-3 ${isActive
                                                                ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                                                                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                                                            }`}
                                                    >
                                                        <span className="text-xs">
                                                            {lesson.resource_type === 'video' ? '🎥' : '📝'}
                                                        </span>
                                                        <span className="truncate">{lesson.title}</span>
                                                    </Link>
                                                );
                                            })}
                                        </div>
                                    ) : (
                                        <div className="p-4 text-xs text-center text-gray-500">
                                            No lessons available
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
