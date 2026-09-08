'use client';

import { useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores/authStore';
import { useCurrentUser } from '@/lib/hooks/useAuth';

interface AuthGuardProps {
  children: React.ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  // _hasHydrated is set to true by Zustand's persist middleware after it reads localStorage
  const token = useAuthStore((s) => s.token);
  const hasHydrated = useAuthStore((s) => s._hasHydrated);

  // Rehydrate user profile from token if page was refreshed
  useCurrentUser();

  useEffect(() => {
    // Only redirect once Zustand has finished reading from localStorage
    if (hasHydrated && !token) {
      router.replace('/login');
    }
  }, [hasHydrated, token, router]);

  // Still reading localStorage — render nothing yet
  if (!hasHydrated) return null;

  // Hydrated but no token → redirect in progress
  if (!token) return null;

  return <>{children}</>;
}
