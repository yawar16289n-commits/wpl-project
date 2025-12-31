'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { userApi } from '@/lib/api';
import Header from '@/app/components/Header';
import Link from 'next/link';
import Image from 'next/image';

export default function PublicProfile() {
  const params = useParams();
  const router = useRouter();
  const userId = params.id ? parseInt(params.id as string) : null;

  const [profile, setProfile] = useState<{
    id: number;
    name: string;
    role: string;
    bio?: string;
    profile_picture?: string;
    courses?: Array<{
      id: number;
      title: string;
      description: string;
      category: string;
      level: string;
      rating: number;
      total_students: number;
      image?: string;
    }>;
    total_courses?: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!userId) {
      setError('Invalid user ID');
      setLoading(false);
      return;
    }

    const fetchProfile = async () => {
      const response = await userApi.getPublicProfile(userId);
      
      if (response.success && (response.data as { success: boolean; profile: Record<string, unknown> })?.success) {
        const profileData = (response.data as { success: boolean; profile: Record<string, unknown> }).profile as typeof profile;
        setProfile(profileData);
      } else {
        setError(response.error || 'Failed to load profile');
      }
      setLoading(false);
    };

    fetchProfile();
  }, [userId, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Profile Not Found</h2>
            <p className="text-gray-600 mb-6">{error || 'This profile does not exist.'}</p>
            <Link href="/" className="text-blue-600 hover:text-blue-700 font-medium">
              Return to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="bg-white rounded-lg shadow-sm">
          <div className="p-8 border-b border-gray-200">
            <div className="flex items-start gap-6">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-3xl font-bold flex-shrink-0">
                {profile.name?.charAt(0).toUpperCase() || 'U'}
              </div>
 

              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{profile.name}</h1>
                <div className="flex items-center gap-3 mb-4">
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                    profile.role === 'instructor' 
                      ? 'bg-purple-100 text-purple-700' 
                      : profile.role === 'admin'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-blue-100 text-blue-700'
                  }`}>
                    {profile.role.charAt(0).toUpperCase() + profile.role.slice(1)}
                  </span>
                  {profile.role === 'instructor' && profile.total_courses !== undefined && (
                    <span className="text-gray-600">
                      {profile.total_courses} {profile.total_courses === 1 ? 'Course' : 'Courses'}
                    </span>
                  )}
                </div>
                {profile.bio && (
                  <p className="text-gray-700 leading-relaxed">{profile.bio}</p>
                )}
              </div>
            </div>
          </div>

          {profile.role === 'instructor' && profile.courses && profile.courses.length > 0 && (
            <div className="p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Courses by {profile.name}</h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {profile.courses.map((course) => (
                  <Link key={course.id} href={`/course/${course.id}`}>
                    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
                      {course.image && (
                        <Image 
                          src={course.image} 
                          alt={course.title}
                          width={400}
                          height={200}
                          className="w-full h-40 object-cover"
                        />
                      )}
                      <div className="p-4">
                        <h3 className="font-bold text-gray-900 mb-2 line-clamp-2">{course.title}</h3>
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{course.description}</p>
                        
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center gap-1">
                            <span className="text-yellow-500">★</span>
                            <span className="font-medium">{course.rating.toFixed(1)}</span>
                          </div>
                          <span className="text-gray-500">{course.total_students.toLocaleString()} students</span>
                        </div>

                        <div className="mt-3 flex items-center justify-between">
                          <span className="text-xs text-gray-500 uppercase">{course.level}</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
