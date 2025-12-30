'use client';

import { useState, useEffect } from 'react';
import { userApi } from '@/lib/api';
import Header from '@/app/components/Header';
import Link from 'next/link';

export default function AccountProfile() {
  const [user, setUser] = useState<{ id: number; name: string; email: string; role: string } | null>(null);
  const [profile, setProfile] = useState<{
    name: string;
    email: string;
    role: string;
    bio?: string;
    profile_picture?: string;
    created_at: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    bio: '',
    profile_picture: '',
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        setLoading(false);
        return;
      }
      const userData = JSON.parse(userStr);
      setUser(userData);

      const response = await userApi.getMyProfile(userData.id);
      if (response.success && (response.data as { success: boolean; profile: Record<string, unknown> })?.success) {
        const profileData = (response.data as { success: boolean; profile: Record<string, unknown> }).profile as typeof profile;
        setProfile(profileData);
        setFormData({
          name: (profileData?.name as string) || '',
          bio: (profileData?.bio as string) || '',
          profile_picture: (profileData?.profile_picture as string) || '',
        });
      }
      setLoading(false);
    };

    fetchProfile();
  }, []);

  const handleEdit = () => {
    setEditing(true);
    setMessage('');
  };

  const handleCancel = () => {
    setEditing(false);
    setFormData({
      name: profile?.name || '',
      bio: profile?.bio || '',
      profile_picture: profile?.profile_picture || '',
    });
    setMessage('');
  };

  const handleSave = async () => {
    const userStr = localStorage.getItem('user');
    if (!userStr) return;
    const user = JSON.parse(userStr);

    setSaving(true);
    setMessage('');

    const response = await userApi.updateProfile(user.id, formData);

    if (response.success && (response.data as { success: boolean; profile: Record<string, unknown> })?.success) {
      const updatedProfile = (response.data as { success: boolean; profile: Record<string, unknown> }).profile as typeof profile;
      setProfile(updatedProfile);
      setEditing(false);
      setMessage('Profile updated successfully!');
      
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        userData.name = updatedProfile?.name;
        userData.bio = updatedProfile?.bio;
        userData.profile_picture = updatedProfile?.profile_picture;
        localStorage.setItem('user', JSON.stringify(userData));
      }
    } else {
      setMessage(response.error || 'Failed to update profile');
    }

    setSaving(false);
  };

  if (loading) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </>
    );
  }

  return (
    <main className="min-h-screen bg-white">
      <Header />

      <div className="bg-gray-50 border-b">
        <div className="max-w-7xl mx-auto px-6 py-3">
          <p className="text-sm text-gray-600">
            <Link href="/dashboard" className="hover:text-gray-900">Home</Link>
            {' / '}
            <span className="text-gray-900 font-medium">Account</span>
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <h3 className="text-lg font-bold text-gray-900 mb-6">Settings</h3>
              <nav className="space-y-1">
                <a href="#" className="block px-4 py-3 text-blue-600 bg-blue-50 rounded-lg font-medium border-l-4 border-blue-600">
                  General Information
                </a>
                <Link href={`/profile/${user?.id}`} className="block px-4 py-3 text-green-700 bg-green-50 hover:bg-green-100 rounded-lg font-medium mt-4">
                  View Public Profile
                </Link>
              </nav>
            </div>
          </div>

          <div className="lg:col-span-3">
            {message && (
              <div className={`mb-6 p-4 rounded-md ${message.includes('success') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
                {message}
              </div>
            )}

            <div className="bg-white">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900">General Information</h2>
                  <p className="text-gray-600 mt-1">Update your personal information</p>
                </div>
                {!editing ? (
                  <button 
                    onClick={handleEdit}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700"
                  >
                    Edit
                  </button>
                ) : (
                  <div className="flex gap-3">
                    <button 
                      onClick={handleCancel}
                      className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50"
                      disabled={saving}
                    >
                      Cancel
                    </button>
                    <button 
                      onClick={handleSave}
                      disabled={saving}
                      className="px-6 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
                    >
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                )}
              </div>

              <div className="mb-8 pb-8 border-b border-gray-200">
                <div className="flex items-start gap-6">
                  <div className="w-28 h-28 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold text-4xl">
                    {profile?.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">Profile Photo</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      {profile?.role === 'instructor' ? 'Instructor' : 'Student'} • {profile?.email}
                    </p>
                    {editing && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Profile Picture URL (optional)
                        </label>
                        <input
                          type="text"
                          value={formData.profile_picture}
                          onChange={(e) => setFormData({ ...formData, profile_picture: e.target.value })}
                          placeholder="https://example.com/image.jpg"
                          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                  <input
                    type="text"
                    value={editing ? formData.name : profile?.name || ''}
                    onChange={(e) => editing && setFormData({ ...formData, name: e.target.value })}
                    disabled={!editing}
                    className={`w-full px-4 py-2 border border-gray-300 rounded-md ${!editing ? 'bg-gray-50 text-gray-600 cursor-not-allowed' : 'focus:outline-none focus:ring-2 focus:ring-blue-500'}`}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input
                    type="email"
                    value={profile?.email || ''}
                    disabled
                    className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600 cursor-not-allowed"
                  />
                  <p className="mt-1 text-sm text-gray-500">Email cannot be changed</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Account Type</label>
                  <input
                    type="text"
                    value={profile?.role === 'instructor' ? 'Instructor' : profile?.role === 'admin' ? 'Admin' : 'Student'}
                    disabled
                    className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600 cursor-not-allowed capitalize"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
                  <textarea
                    value={editing ? formData.bio : profile?.bio || ''}
                    onChange={(e) => editing && setFormData({ ...formData, bio: e.target.value })}
                    disabled={!editing}
                    rows={4}
                    placeholder="Tell us about yourself..."
                    className={`w-full px-4 py-2 border border-gray-300 rounded-md ${!editing ? 'bg-gray-50 text-gray-600 cursor-not-allowed' : 'focus:outline-none focus:ring-2 focus:ring-blue-500'}`}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Member Since</label>
                  <input
                    type="text"
                    value={profile?.created_at ? new Date(profile.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : ''}
                    disabled
                    className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600 cursor-not-allowed"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
