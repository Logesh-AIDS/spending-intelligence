'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useRegister } from '@/lib/hooks/useAuth';
import { useAuthStore } from '@/lib/stores/authStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

type ServerStatus = 'checking' | 'ready' | 'waking' | 'unreachable';

function useServerStatus() {
  const [status, setStatus] = useState<ServerStatus>('checking');

  useEffect(() => {
    const url = (process.env.NEXT_PUBLIC_API_URL || '').replace('/api/v1', '');
    if (!url) { setStatus('ready'); return; }

    let cancelled = false;

    const ping = async (attempt = 1): Promise<void> => {
      try {
        const res = await fetch(`${url}/health`, { method: 'GET', cache: 'no-store' });
        if (!cancelled) setStatus(res.ok ? 'ready' : 'unreachable');
      } catch {
        if (cancelled) return;
        if (attempt <= 6) {
          setStatus('waking');
          setTimeout(() => ping(attempt + 1), 8000);
        } else {
          setStatus('unreachable');
        }
      }
    };

    ping();
    return () => { cancelled = true; };
  }, []);

  return status;
}

export default function RegisterPage() {
  const router = useRouter();
  const [full_name, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { mutate: register, isPending, error } = useRegister();
  const setToken = useAuthStore((s) => s.setToken);
  const setUser = useAuthStore((s) => s.setUser);
  const serverStatus = useServerStatus();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    register(
      { full_name, email, password },
      {
        onSuccess: ({ token, user }) => {
          setToken(token);
          setUser(user);
          setTimeout(() => router.push('/dashboard'), 50);
        },
      }
    );
  };

  const getErrorMessage = () => {
    if (!error) return null;
    const axiosErr = error as any;
    const isNetworkError = !axiosErr?.response;
    if (isNetworkError) return 'The server is still waking up. Please wait a moment and try again.';
    return axiosErr?.response?.data?.detail || error.message || 'Registration failed. Please try again.';
  };

  const isServerReady = serverStatus === 'ready';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <Card className="p-8 w-full max-w-md">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Create Account</h1>
          <p className="text-slate-600 mt-2">Start taking control of your spending today</p>
        </div>

        {/* Server status banner */}
        {serverStatus === 'checking' && (
          <div className="mb-4 flex items-center gap-2 text-sm text-slate-500 bg-slate-50 border border-slate-200 rounded px-3 py-2">
            <span className="inline-block w-2 h-2 rounded-full bg-slate-400 animate-pulse" />
            Connecting to server…
          </div>
        )}
        {serverStatus === 'waking' && (
          <div className="mb-4 flex items-center gap-2 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
            <span className="inline-block w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            Server is waking up — this takes about 30 seconds. Please wait…
          </div>
        )}
        {serverStatus === 'ready' && (
          <div className="mb-4 flex items-center gap-2 text-sm text-green-700 bg-green-50 border border-green-200 rounded px-3 py-2">
            <span className="inline-block w-2 h-2 rounded-full bg-green-500" />
            Server is ready
          </div>
        )}
        {serverStatus === 'unreachable' && (
          <div className="mb-4 flex items-center gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded px-3 py-2">
            <span className="inline-block w-2 h-2 rounded-full bg-red-500" />
            Cannot reach server. Check your internet connection.
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="full_name">Full Name</Label>
            <Input
              id="full_name"
              type="text"
              placeholder="John Doe"
              value={full_name}
              onChange={(e) => setFullName(e.target.value)}
              required
              autoComplete="name"
            />
          </div>
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
              minLength={6}
              autoComplete="new-password"
            />
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {getErrorMessage()}
            </div>
          )}

          <Button
            type="submit"
            disabled={isPending || !isServerReady}
            className="w-full"
          >
            {isPending
              ? 'Creating account…'
              : serverStatus === 'checking' || serverStatus === 'waking'
              ? 'Waiting for server…'
              : 'Sign Up'}
          </Button>
        </form>

        <div className="mt-6 pt-6 border-t">
          <p className="text-center text-slate-600 text-sm">
            Already have an account?{' '}
            <Link href="/login" className="text-blue-600 hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
}
