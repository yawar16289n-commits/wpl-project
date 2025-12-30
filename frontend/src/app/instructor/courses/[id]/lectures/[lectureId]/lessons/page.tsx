'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Header from '@/app/components/Header';
import { lectureApi, lectureResourceApi } from '@/lib/api';

export default function ManageLectureLessons() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.id as string;
  const lectureId = params.lectureId as string;
  
  const [lecture, setLecture] = useState<any>(null);
  const [lessons, setLessons] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingLesson, setEditingLesson] = useState<any>(null);
  const [formData, setFormData] = useState({
    lesson_type: 'video',
    title: '',
    url: '',
    content: '',
    duration: '',
    order: '',
  });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchLectureAndLessons();
  }, [lectureId]);

  const fetchLectureAndLessons = async () => {
    try {
      setLoading(true);
      
      // Fetch lecture
      const lectureRes = await lectureApi.getLecture(Number(lectureId));
      if (lectureRes.success && lectureRes.data) {
        setLecture((lectureRes.data as any).lecture);
      }

      // Fetch lessons (using resource API but treating as lessons)
      const lessonsRes = await lectureResourceApi.getLectureResources(Number(lectureId));
      if (lessonsRes.success && lessonsRes.data) {
        setLessons((lessonsRes.data as any).resources || []);
      }
    } catch (err) {
      setError('Failed to load lecture lessons');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    const lessonData = {
      lecture_id: Number(lectureId),
      resource_type: formData.lesson_type as any,
      title: formData.title,
      url: formData.url || undefined,
      content: formData.content || undefined,
      duration: formData.duration || undefined,
      order: parseInt(formData.order) || lessons.length + 1,
    };

    const response = editingLesson
      ? await lectureResourceApi.updateResource(editingLesson.id, lessonData)
      : await lectureResourceApi.createResource(lessonData);

    if (response.success) {
      setMessage(editingLesson ? 'Lesson updated!' : 'Lesson added!');
      setShowAddModal(false);
      setEditingLesson(null);
      setFormData({ lesson_type: 'video', title: '', url: '', content: '', duration: '', order: '' });
      fetchLectureAndLessons();
    } else {
      setError(response.error || 'Failed to save lesson');
    }
  };

  const handleEdit = (lesson: any) => {
    setEditingLesson(lesson);
    setFormData({
      lesson_type: lesson.resource_type,
      title: lesson.title,
      url: lesson.url || '',
      content: lesson.content || '',
      duration: lesson.duration || '',
      order: lesson.order?.toString() || '',
    });
    setShowAddModal(true);
  };

  const handleDelete = async (lessonId: number) => {
    if (!confirm('Delete this lesson?')) return;

    const response = await lectureResourceApi.deleteResource(lessonId);
    if (response.success) {
      setMessage('Lesson deleted!');
      fetchLectureAndLessons();
    } else {
      setError(response.error || 'Failed to delete');
    }
  };

  const closeModal = () => {
    setShowAddModal(false);
    setEditingLesson(null);
    setFormData({ lesson_type: 'video', title: '', url: '', content: '', duration: '', order: '' });
    setError('');
  };

  const getLessonIcon = (type: string) => {
    return type === 'video' ? '🎥' : '📝';
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
        {/* Breadcrumb */}
        <div className="mb-6">
          <Link href="/dashboard" className="text-blue-600 hover:underline">Dashboard</Link>
          <span className="mx-2">/</span>
          <Link href={`/instructor/courses/${courseId}/lectures`} className="text-blue-600 hover:underline">
            Lectures
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-600">Lessons</span>
        </div>

        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Lecture Lessons</h1>
            <p className="text-gray-600 mt-1">{lecture?.title}</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Lesson
          </button>
        </div>

        {/* Messages */}
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

        {/* Lessons List */}
        <div className="space-y-4">
          {lessons.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No Lessons Yet</h3>
              <p className="text-gray-500 mb-4">Add video or text lessons for this lecture</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
              >
                Add First Lesson
              </button>
            </div>
          ) : (
            lessons.map((lesson, index) => (
              <div key={lesson.id || index} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start">
                  <div className="flex items-start gap-4 flex-1">
                    <span className="text-4xl">{getLessonIcon(lesson.resource_type)}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`${lesson.resource_type === 'video' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'} text-xs font-semibold px-2 py-1 rounded`}>
                          {lesson.resource_type === 'video' ? 'VIDEO' : 'TEXT'}
                        </span>
                        <h3 className="text-lg font-bold text-gray-900">{lesson.title}</h3>
                      </div>
                      {lesson.resource_type === 'video' && lesson.url && (
                        <a href={lesson.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm block mb-1">
                          {lesson.url}
                        </a>
                      )}
                      {lesson.resource_type === 'text' && lesson.content && (
                        <p className="text-gray-600 text-sm mb-1">{lesson.content.substring(0, 150)}{lesson.content.length > 150 ? '...' : ''}</p>
                      )}
                      {lesson.duration && (
                        <span className="text-sm text-gray-500">⏱️ {lesson.duration}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(lesson)}
                      className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 text-sm"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(lesson.id)}
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

      {/* Add/Edit Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {editingLesson ? 'Edit Lesson' : 'Add New Lesson'}
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
                    Lesson Type *
                  </label>
                  <select
                    required
                    value={formData.lesson_type}
                    onChange={(e) => setFormData({ ...formData, lesson_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="video">Video Lesson</option>
                    <option value="text">Text Lesson</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Introduction Video"
                  />
                </div>

                {formData.lesson_type === 'video' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Video URL *
                    </label>
                    <input
                      type="url"
                      required={formData.lesson_type === 'video'}
                      value={formData.url}
                      onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="https://www.youtube.com/watch?v=..."
                    />
                    <p className="text-xs text-gray-500 mt-1">YouTube, Vimeo, or direct video link</p>
                  </div>
                )}

                {formData.lesson_type === 'text' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Content *
                    </label>
                    <textarea
                      rows={8}
                      required={formData.lesson_type === 'text'}
                      value={formData.content}
                      onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Write your lesson content here..."
                    />
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Duration
                    </label>
                    <input
                      type="text"
                      value={formData.duration}
                      onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., 15 min"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Order
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={formData.order}
                      onChange={(e) => setFormData({ ...formData, order: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="1"
                    />
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700"
                  >
                    {editingLesson ? 'Update Lesson' : 'Add Lesson'}
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
