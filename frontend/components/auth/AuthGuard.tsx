'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores/authStore';
import { useCurrentUser } from '@/lib/hooks/useAuth';

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const token = useAuthStore((s) => s.token);
  const hasHydrated = useAuthStore((s) => s._hasHydrated);
  // Safety net: if hydration never fires (SSR edge case), unblock after 300ms
  const [timedOut, setTimedOut] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setTimedOut(true), 300);
    return () => clearTimeout(t);
  }, []);

  // Rehydrate user profile from stored token on page refresh
  useCurrentUser();

  const ready = hasHydrated || timedOut;

  useEffect(() => {
    if (ready && !token) {
      router.replace('/login');
    }
  }, [ready, token, router]);

  // Not ready yet — show nothing (avoids flash of protected content)
  if (!ready) return null;

  // Ready but no token — redirect in flight, show nothing
  if (!token) return null;

  return <>{children}</>;
}
