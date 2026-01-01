'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Header from '@/app/components/Header';
import { courseApi, lectureApi, lectureResourceApi } from '@/lib/api';

export default function ManageCourseLectures() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.id as string;
  
  const [course, setCourse] = useState<any>(null);
  const [lectures, setLectures] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingLecture, setEditingLecture] = useState<any>(null);
  const [formData, setFormData] = useState({
    title: '',
    duration: '',
  });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchCourseAndLectures();
  }, [courseId]);

  const fetchCourseAndLectures = async () => {
    try {
      setLoading(true);
      
      const courseRes = await courseApi.getCourse(Number(courseId));
      if (courseRes.success && courseRes.data) {
        setCourse((courseRes.data as any).course);
      }

      const lecturesRes = await lectureApi.getCourseLectures(Number(courseId));
      if (lecturesRes.success && lecturesRes.data) {
        setLectures((lecturesRes.data as any).lectures || []);
      }
    } catch (err) {
      setError('Failed to load course lectures');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    const lectureData = {
      course_id: Number(courseId),
      number: editingLecture ? editingLecture.number : lectures.length + 1,
      title: formData.title,
      lessons: 0,
      duration: formData.duration,
    };

    const response = editingLecture
      ? await lectureApi.updateLecture(editingLecture.id, lectureData)
      : await lectureApi.createLecture(lectureData);

    if (response.success) {
      setMessage(editingLecture ? 'Lecture updated!' : 'Lecture added!');
      setShowAddModal(false);
      setEditingLecture(null);
      setFormData({ title: '', duration: '' });
      fetchCourseAndLectures();
    } else {
      setError(response.error || 'Failed to save lecture');
    }
  };

  const handleEdit = (lecture: any) => {
    setEditingLecture(lecture);
    setFormData({
      title: lecture.title,
      duration: lecture.duration || '',
    });
    setShowAddModal(true);
  };

  const handleDelete = async (lectureId: number) => {
    if (!confirm('Delete this lecture? This will also delete all its resources.')) return;

    const response = await lectureApi.deleteLecture(lectureId);
    if (response.success) {
      setMessage('Lecture deleted!');
      fetchCourseAndLectures();
    } else {
      setError(response.error || 'Failed to delete');
    }
  };

  const closeModal = () => {
    setShowAddModal(false);
    setEditingLecture(null);
    setFormData({ title: '', duration: '' });
    setError('');
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
        <div className="mb-6">
          <Link href="/dashboard" className="text-blue-600 hover:underline">Dashboard</Link>
          <span className="mx-2">/</span>
          <Link href={`/instructor/courses/${courseId}/edit`} className="text-blue-600 hover:underline">
            {course?.title}
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-600">Lectures</span>
        </div>

        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Course Lectures</h1>
            <p className="text-gray-600 mt-1">Manage modules and lessons for {course?.title}</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Lecture
          </button>
        </div>

        {message && (
          <div className="mb-4 p-4 bg-green-100 text-green-800 rounded-lg">
            {message}
          </div>
        )}
        {error && (
          <div className="mb-4 p-4 bg-red-100 text-red-800 rounded-lg">
            {error}
          </div>
        )}

        <div className="space-y-4">
          {lectures.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No Lectures Yet</h3>
              <p className="text-gray-500 mb-4">Start building your course by adding lectures</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
              >
                Add First Lecture
              </button>
            </div>
          ) : (
            lectures.map((lecture, index) => (
              <div key={lecture.id || index} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded-full">
                        Module {lecture.number}
                      </span>
                      <h3 className="text-xl font-bold text-gray-900">{lecture.title}</h3>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600">
                      <span>📚 {lecture.lessons} lessons</span>
                      <span>⏱️ {lecture.duration}</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Link
                      href={`/instructor/courses/${courseId}/lectures/${lecture.id}/lessons`}
                      className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 text-sm"
                    >
                      Manage Lessons
                    </Link>
                    <button
                      onClick={() => handleEdit(lecture)}
                      className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 text-sm"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(lecture.id)}
                      className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {editingLecture ? 'Edit Lecture' : 'Add New Lecture'}
                </h2>
                <button onClick={closeModal} className="text-gray-500 hover:text-gray-700">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-100 text-red-800 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Lecture Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Introduction to Python"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duration
                  </label>
                  <input
                    type="text"
                    value={formData.duration}
                    onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 2 hours"
                  />
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <strong>ℹ️ Note:</strong> The number of lessons will be calculated automatically based on how many resources you add to this lecture.
                  </p>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700"
                  >
                    {editingLecture ? 'Update Lecture' : 'Add Lecture'}
                  </button>
                  <button
                    type="button"
                    onClick={closeModal}
                    className="px-6 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
