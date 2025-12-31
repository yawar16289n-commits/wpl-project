// User role utility functions

export type UserRole = 'learner' | 'instructor' | 'admin';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  profile_picture?: string;
  bio?: string;
  created_at?: string;
}

/**
 * Get current user from localStorage
 */
export function getCurrentUser(): User | null {
  if (typeof window === 'undefined') return null;
  
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  
  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
}

/**
 * Check if current user has a specific role
 */
export function hasRole(role: UserRole): boolean {
  const user = getCurrentUser();
  return user?.role === role;
}

/**
 * Check if current user is an instructor
 */
export function isInstructor(): boolean {
  return hasRole('instructor');
}

/**
 * Check if current user is a learner
 */
export function isLearner(): boolean {
  return hasRole('learner');
}

/**
 * Check if current user is an admin
 */
export function isAdmin(): boolean {
  return hasRole('admin');
}

/**
 * Check if user can enroll in courses
 * Only learners can enroll (not instructors or admins)
 */
export function canEnroll(): boolean {
  const user = getCurrentUser();
  if (!user) return false;
  return user.role === 'learner';
}

/**
 * Check if user can submit reviews/ratings
 * Only learners can review (not instructors or admins)
 */
export function canReview(): boolean {
  const user = getCurrentUser();
  if (!user) return false;
  return user.role === 'learner';
}

/**
 * Check if user can create courses
 * Only instructors can create courses (not admins)
 */
export function canCreateCourse(): boolean {
  const user = getCurrentUser();
  if (!user) return false;
  return user.role === 'instructor';
}

/**
 * Get role display name
 */
export function getRoleDisplayName(role: UserRole): string {
  const roleNames: Record<UserRole, string> = {
    learner: 'Student',
    instructor: 'Instructor',
    admin: 'Administrator'
  };
  return roleNames[role] || role;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getCurrentUser() !== null;
}

/**
 * Get user ID
 */
export function getUserId(): number | null {
  const user = getCurrentUser();
  return user?.id || null;
}

/**
 * Save user to localStorage
 */
export function saveUser(user: User): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('user', JSON.stringify(user));
}

/**
 * Clear user from localStorage (logout)
 */
export function clearUser(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('user');
}
