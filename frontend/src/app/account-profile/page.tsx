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
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [passwordMessage, setPasswordMessage] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

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

  const handlePasswordUpdate = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setPasswordMessage('New passwords do not match');
      return;
    }

    if (passwordData.new_password.length < 6) {
      setPasswordMessage('Password must be at least 6 characters');
      return;
    }

    const userStr = localStorage.getItem('user');
    if (!userStr) return;
    const user = JSON.parse(userStr);

    setSaving(true);
    setPasswordMessage('');

    const response = await userApi.updateProfile(user.id, {
      password: passwordData.new_password,
      current_password: passwordData.current_password,
    });

    if (response.success) {
      setPasswordMessage('Password updated successfully!');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } else {
      setPasswordMessage(response.error || 'Failed to update password');
    }

    setSaving(false);
  };

  const handleDeleteAccount = async () => {
    const userStr = localStorage.getItem('user');
    if (!userStr) return;
    const user = JSON.parse(userStr);

    setSaving(true);
    const response = await userApi.deleteUser(user.id);

    if (response.success) {
      localStorage.removeItem('user');
      window.location.href = '/';
    } else {
      setMessage(response.error || 'Failed to delete account');
      setShowDeleteConfirm(false);
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

              {/* Password Update Section */}
              <div className="mt-12 pt-8 border-t border-gray-200">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Change Password</h3>
                {passwordMessage && (
                  <div className={`mb-4 p-4 rounded-md ${
                    passwordMessage.includes('success') 
                      ? 'bg-green-50 text-green-800 border border-green-200' 
                      : 'bg-red-50 text-red-800 border border-red-200'
                  }`}>
                    {passwordMessage}
                  </div>
                )}
                <div className="space-y-4 max-w-md">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                    <input
                      type="password"
                      value={passwordData.current_password}
                      onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
                    <input
                      type="password"
                      value={passwordData.new_password}
                      onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                    <input
                      type="password"
                      value={passwordData.confirm_password}
                      onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button
                    onClick={handlePasswordUpdate}
                    disabled={saving || !passwordData.current_password || !passwordData.new_password || !passwordData.confirm_password}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {saving ? 'Updating...' : 'Update Password'}
                  </button>
                </div>
              </div>

              {/* Delete Account Section */}
              <div className="mt-12 pt-8 border-t border-gray-200">
                <h3 className="text-xl font-bold text-red-600 mb-2">Danger Zone</h3>
                <p className="text-gray-600 mb-4">Once you delete your account, there is no going back. Please be certain.</p>
                
                {!showDeleteConfirm ? (
                  <button
                    onClick={() => setShowDeleteConfirm(true)}
                    className="px-6 py-2 bg-red-600 text-white rounded-md font-medium hover:bg-red-700"
                  >
                    Delete Account
                  </button>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
                    <h4 className="font-bold text-red-900 mb-2">Are you absolutely sure?</h4>
                    <p className="text-sm text-red-800 mb-4">
                      This action cannot be undone. This will permanently delete your account and remove all your data from our servers.
                    </p>
                    <div className="flex gap-3">
                      <button
                        onClick={() => setShowDeleteConfirm(false)}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50"
                        disabled={saving}
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleDeleteAccount}
                        disabled={saving}
                        className="px-4 py-2 bg-red-600 text-white rounded-md font-medium hover:bg-red-700 disabled:opacity-50"
                      >
                        {saving ? 'Deleting...' : 'Yes, Delete My Account'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
