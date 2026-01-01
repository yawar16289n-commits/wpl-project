'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Header from '@/app/components/Header';
import Footer from '@/app/components/Footer';
import CourseCard from '@/app/components/CourseCard';
import { courseApi } from '@/lib/api';

interface Course {
  id: number;
  title: string;
  description: string;
  image: string;
  instructor?: string;
  company?: string;
  category?: string;
  rating: number;
  students: number;
  level: string;
  duration: string;
}

export default function SearchPage() {
  const searchParams = useSearchParams();
  const searchQuery = searchParams.get('q') || '';
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedLevel, setSelectedLevel] = useState<string>('');
  const [allCourses, setAllCourses] = useState<Course[]>([]);

  useEffect(() => {
    const fetchAllCourses = async () => {
      try {
        const response = await courseApi.getCourses();
        if (response.success && response.data) {
          const coursesData = (response.data as { courses: Course[] }).courses;
          setAllCourses(coursesData);
        }
      } catch (error) {
        console.error('Error fetching all courses:', error);
      }
    };
    fetchAllCourses();
  }, []);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        const filters: { q?: string; category?: string; level?: string } = {};
        
        if (searchQuery) filters.q = searchQuery;
        if (selectedCategory) filters.category = selectedCategory;
        if (selectedLevel) filters.level = selectedLevel;

        const response = await courseApi.getCourses(filters);
        if (response.success && response.data) {
          const coursesData = (response.data as { courses: Course[] }).courses;
          setCourses(coursesData);
        }
      } catch (error) {
        console.error('Error fetching courses:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [searchQuery, selectedCategory, selectedLevel]);

  const categories = Array.from(new Set(allCourses.map(c => c.category).filter(Boolean)));
  const levels = ['Beginner', 'Intermediate', 'Advanced'];

  return (
    <main className="min-h-screen bg-white">
      <Header />
      
      <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
              {searchQuery ? `Search results for "${searchQuery}"` : 'Search Courses'}
            </h1>
            <p className="text-gray-600 text-lg">
              {loading ? 'Searching...' : `Found ${courses.length} course${courses.length !== 1 ? 's' : ''}`}
            </p>
          </div>

          <div className="mb-8 flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[200px]"
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Level</label>
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[200px]"
              >
                <option value="">All Levels</option>
                {levels.map(level => (
                  <option key={level} value={level}>
                    {level}
                  </option>
                ))}
              </select>
            </div>

            {(selectedCategory || selectedLevel) && (
              <button
                onClick={() => {
                  setSelectedCategory('');
                  setSelectedLevel('');
                }}
                className="px-4 py-2 text-sm text-blue-600 hover:text-blue-800 self-end"
              >
                Clear Filters
              </button>
            )}
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : courses.length > 0 ? (
            <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {courses.map((course) => (
                <CourseCard 
                  key={course.id} 
                  id={course.id.toString()} 
                  title={course.title} 
                  image={course.image || '/placeholder.svg'}
                  instructor={course.instructor || course.company}
                  rating={course.rating}
                  students={course.students}
                  level={course.level}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-white rounded-lg shadow-sm">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <p className="text-gray-600 text-lg mb-2">
                {searchQuery ? `No courses found matching "${searchQuery}"` : 'Enter a search term to find courses'}
              </p>
              <p className="text-gray-500 text-sm">
                Try searching for different keywords or browse all courses
              </p>
            </div>
          )}
        </div>
      </section>

      <Footer />
    </main>
  );
}
