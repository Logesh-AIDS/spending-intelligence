'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { TrendingDown, BarChart3, Lock } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 bg-white shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">SpendControl</h1>
        <div className="flex gap-4">
          <Link href="/login">
            <Button variant="outline">Sign In</Button>
          </Link>
          <Link href="/register">
            <Button>Get Started</Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-slate-900 mb-4">
            Take Control of Your Spending
          </h2>
          <p className="text-xl text-slate-600 mb-8">
            Smart financial management made simple. Track expenses, visualize trends, and reach your financial goals.
          </p>
          <Link href="/register">
            <Button size="lg">Start Free Today</Button>
          </Link>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 py-12">
          <div className="p-8 bg-white rounded-lg shadow-sm">
            <BarChart3 className="w-12 h-12 text-blue-600 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Smart Dashboard</h3>
            <p className="text-slate-600">
              Get a complete overview of your finances with beautiful charts and real-time insights.
            </p>
          </div>

          <div className="p-8 bg-white rounded-lg shadow-sm">
            <TrendingDown className="w-12 h-12 text-green-600 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Track Spending</h3>
            <p className="text-slate-600">
              Categorize transactions and understand your spending patterns at a glance.
            </p>
          </div>

          <div className="p-8 bg-white rounded-lg shadow-sm">
            <Lock className="w-12 h-12 text-purple-600 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Secure & Private</h3>
            <p className="text-slate-600">
              Your financial data is encrypted and secure. We never share your information.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
