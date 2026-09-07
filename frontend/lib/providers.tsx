'use client';

import { ReactNode, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      gcTime: 1000 * 60 * 5, // 5 minutes (formerly cacheTime)
      retry: 1,
    },
  },
});

// Silently wakes up the Render free-tier backend on app load.
// Render spins down after 15 min idle; this ping fires immediately so
// the server is warm by the time the user submits a form (~30-50s head start).
function WakeUpBackend() {
  useEffect(() => {
    const url = (process.env.NEXT_PUBLIC_API_URL || '').replace('/api/v1', '');
    if (!url) return;
    fetch(`${url}/health`, { method: 'GET' }).catch(() => {
      // Silently ignore — this is best-effort only
    });
  }, []);
  return null;
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <WakeUpBackend />
      {children}
    </QueryClientProvider>
  );
}
