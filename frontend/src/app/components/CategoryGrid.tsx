'use client';

import { useEffect, useState } from 'react';
import CourseCard from "./CourseCard";
import { courseApi } from '@/lib/api';

interface Course {
  id: number;
  title: string;
  description: string;
  image: string;
  instructor?: string;
  company?: string;
  price: number;
  rating: number;
  students: number;
  level: string;
  duration: string;
}

export default function CategoryGrid() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await courseApi.getCourses();
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
  }, []);

  if (loading) {
    return (
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-6">
        
        <div className="mb-12">
          <h3 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
            Explore popular courses
          </h3>
          <p className="text-gray-600 text-lg">Trending skills with high demand and competitive salaries</p>
        </div>

        {courses.length > 0 ? (
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6">
            {courses.map((course) => (
              <CourseCard 
                key={course.id} 
                id={course.id.toString()} 
                title={course.title} 
                image={course.image || '/placeholder.svg'}
                instructor={course.instructor || course.company}
                price={course.price}
                rating={course.rating}
                students={course.students}
                level={course.level}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">No courses available at the moment.</p>
          </div>
        )}

      </div>
    </section>
  );
}
