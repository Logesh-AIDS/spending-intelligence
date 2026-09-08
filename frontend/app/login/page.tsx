'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useLogin } from '@/lib/hooks/useAuth';
import { useAuthStore } from '@/lib/stores/authStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { mutate: login, isPending, error } = useLogin();
  const setToken = useAuthStore((s) => s.setToken);
  const setUser = useAuthStore((s) => s.setUser);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(
      { email, password },
      {
        onSuccess: ({ token, user }) => {
          // Explicitly set into store first, then navigate.
          // useLogin's onSuccess also sets these, but calling them here
          // guarantees the store is updated before router.push runs.
          setToken(token);
          setUser(user);
          // Small tick to let Zustand persist to localStorage before navigation
          setTimeout(() => router.push('/dashboard'), 50);
        },
      }
    );
  };

  const getErrorMessage = () => {
    if (!error) return null;
    const axiosErr = error as any;
    const detail = axiosErr?.response?.data?.detail;
    const status = axiosErr?.response?.status;
    const isNetworkError = !axiosErr?.response;

    if (isNetworkError) {
      return `Cannot reach server at ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}. Make sure the backend is running.`;
    }
    if (status === 401) return 'Incorrect email or password.';
    return detail || axiosErr?.message || 'Login failed. Please try again.';
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <Card className="p-8 w-full max-w-md">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Welcome Back</h1>
          <p className="text-slate-600 mt-2">Sign in to your spending control account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {getErrorMessage()}
            </div>
          )}

          <Button type="submit" disabled={isPending} className="w-full">
            {isPending ? 'Signing in…' : 'Sign In'}
          </Button>
        </form>

        <div className="mt-6 pt-6 border-t">
          <p className="text-center text-slate-600 text-sm">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="text-blue-600 hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
}
