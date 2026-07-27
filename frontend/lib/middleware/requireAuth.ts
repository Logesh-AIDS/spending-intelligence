import { redirect } from 'next/navigation';

// This would be used in Server Components to check auth
// For client-side protection, use the useAuth hook

export function requireAuth(token: string | null) {
  if (!token) {
    redirect('/auth/login');
  }
}
