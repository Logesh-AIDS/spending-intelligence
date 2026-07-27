'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores/authStore';
import { useCurrentUser } from '@/lib/hooks/useAuth';

interface AuthGuardProps {
  children: React.ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const { token, isAuthenticated } = useAuthStore();
  const [hydrated, setHydrated] = useState(false);

  // Wait one tick for Zustand to read localStorage before making any decisions
  useEffect(() => {
    setHydrated(true);
  }, []);

  // Rehydrate user profile from token if page was refreshed
  useCurrentUser();

  useEffect(() => {
    if (hydrated && !token) {
      router.replace('/login');
    }
  }, [hydrated, token, router]);

  // Don't render or redirect until hydration is complete
  if (!hydrated) return null;

  // No token after hydration → redirect is in progress, show nothing
  if (!token) return null;

  return <>{children}</>;
}
