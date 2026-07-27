'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores/authStore';
import { useCurrentUser } from '@/lib/hooks/useAuth';

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * Wraps protected pages.
 * - Redirects to /login if no token
 * - Fetches current user if token exists but user not loaded (page refresh)
 * - Shows nothing while loading to prevent flash
 */
export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const { token, user, isAuthenticated } = useAuthStore();

  // Rehydrate user from token on page refresh
  useCurrentUser();

  useEffect(() => {
    if (!token && !isAuthenticated) {
      router.replace('/login');
    }
  }, [token, isAuthenticated, router]);

  // Don't render children until we have confirmed auth
  if (!token && !isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
