'use client';

import { Card } from '@/components/ui/card';
import { StatCard } from '@/components/dashboard/StatCard';
import { TrendChart } from '@/components/dashboard/TrendChart';
import { CategoryChart } from '@/components/dashboard/CategoryChart';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';

// Demo data for unauthenticated users
const demoStats = {
  totalExpenses: 2450.75,
  totalIncome: 4500.00,
  balance: 2049.25,
  monthlyTrend: [
    { month: 'Jan', expenses: 1200, income: 4500 },
    { month: 'Feb', expenses: 1450, income: 4500 },
    { month: 'Mar', expenses: 980, income: 4500 },
    { month: 'Apr', expenses: 1100, income: 4500 },
    { month: 'May', expenses: 2100, income: 4500 },
    { month: 'Jun', expenses: 2450.75, income: 4500 },
  ],
  categoryBreakdown: [
    { name: 'Food', value: 650 },
    { name: 'Transport', value: 400 },
    { name: 'Entertainment', value: 350 },
    { name: 'Utilities', value: 500 },
    { name: 'Other', value: 550.75 },
  ],
};

export default function DashboardPage() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto py-8 px-4">
            <div className="space-y-8">
              <div>
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <p className="text-slate-600">Welcome! Here&apos;s an example of your financial overview.</p>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <StatCard
                  title="Total Expenses"
                  value={demoStats.totalExpenses}
                  trend="up"
                  format="currency"
                />
                <StatCard
                  title="Total Income"
                  value={demoStats.totalIncome}
                  trend="up"
                  format="currency"
                />
                <StatCard
                  title="Balance"
                  value={demoStats.balance}
                  trend={demoStats.balance > 0 ? 'up' : 'down'}
                  format="currency"
                />
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <Card className="p-6">
                  <h2 className="text-lg font-semibold mb-4">Monthly Trend</h2>
                  <TrendChart data={demoStats.monthlyTrend} />
                </Card>

                <Card className="p-6">
                  <h2 className="text-lg font-semibold mb-4">Spending by Category</h2>
                  <CategoryChart data={demoStats.categoryBreakdown} />
                </Card>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
