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

export function hasRole(role: UserRole): boolean {
  const user = getCurrentUser();
  return user?.role === role;
}

export function isInstructor(): boolean {
  return hasRole('instructor');
}

export function isLearner(): boolean {
  return hasRole('learner');
}

export function isAdmin(): boolean {
  return hasRole('admin');
}

export function canEnroll(): boolean {
  const user = getCurrentUser();
  if (!user) return false;
  return user.role === 'learner';
}

export function canReview(): boolean {
  const user = getCurrentUser();
  if (!user) return false;
  return user.role === 'learner';
}

export function canCreateCourse(): boolean {
  const user = getCurrentUser();
  if (!user) return false;
  return user.role === 'instructor';
}

export function getRoleDisplayName(role: UserRole): string {
  const roleNames: Record<UserRole, string> = {
    learner: 'Student',
    instructor: 'Instructor',
    admin: 'Administrator'
  };
  return roleNames[role] || role;
}

export function isAuthenticated(): boolean {
  return getCurrentUser() !== null;
}

export function getUserId(): number | null {
  const user = getCurrentUser();
  return user?.id || null;
}

export function saveUser(user: User): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('user', JSON.stringify(user));
}

export function clearUser(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('user');
}
