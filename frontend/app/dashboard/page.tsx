'use client';

import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { StatCard } from '@/components/dashboard/StatCard';
import { TrendChart } from '@/components/dashboard/TrendChart';
import { CategoryChart } from '@/components/dashboard/CategoryChart';
import { HealthScoreCard } from '@/components/dashboard/HealthScoreCard';
import { RecentTransactions } from '@/components/dashboard/RecentTransactions';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import {
  useDashboardSummary,
  useSpendingTrend,
  useCategoryAnalytics,
  useHealthScore,
} from '@/lib/hooks/useDashboard';

// ── Skeleton while loading ────────────────────────────────────────

function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => <Skeleton key={i} className="h-28 rounded-lg" />)}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Skeleton className="h-80 rounded-lg" />
        <Skeleton className="h-80 rounded-lg" />
      </div>
    </div>
  );
}

// ── Error state ───────────────────────────────────────────────────

function ErrorState({ message }: { message: string }) {
  return (
    <Card className="p-6 text-center text-red-600">
      <p className="font-medium">Failed to load dashboard</p>
      <p className="text-sm mt-1 text-slate-500">{message}</p>
    </Card>
  );
}

// ── Main page ─────────────────────────────────────────────────────

export default function DashboardPage() {
  const summary = useDashboardSummary();
  const trend = useSpendingTrend('monthly');
  const categories = useCategoryAnalytics();
  const health = useHealthScore();

  const isLoading = summary.isLoading || trend.isLoading;
  const isError = summary.isError;

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
                <p className="text-slate-600">Your financial overview at a glance.</p>
              </div>

              {isLoading && <DashboardSkeleton />}

              {isError && (
                <ErrorState message={summary.error?.message || 'Unknown error'} />
              )}

              {!isLoading && !isError && summary.data && (
                <>
                  {/* ── KPI cards ── */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <StatCard
                      title="Current Balance"
                      value={summary.data.current_balance ?? 0}
                      trend={
                        summary.data.net_cash_flow >= 0 ? 'up' : 'down'
                      }
                      format="currency"
                    />
                    <StatCard
                      title="Total Expenses"
                      value={summary.data.total_spending}
                      trend="down"
                      format="currency"
                    />
                    <StatCard
                      title="Total Income"
                      value={summary.data.total_income}
                      trend="up"
                      format="currency"
                    />
                    <StatCard
                      title="Savings Rate"
                      value={summary.data.savings_percentage}
                      trend={summary.data.savings_percentage >= 20 ? 'up' : 'down'}
                      format="percent"
                    />
                  </div>

                  {/* ── Secondary KPIs ── */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <StatCard
                      title="Today's Spending"
                      value={summary.data.today_spending}
                      format="currency"
                    />
                    <StatCard
                      title="This Week"
                      value={summary.data.this_week_spending}
                      format="currency"
                    />
                    <StatCard
                      title="This Month"
                      value={summary.data.this_month_spending}
                      format="currency"
                    />
                    <StatCard
                      title="Avg Daily Spend"
                      value={summary.data.average_daily_spending}
                      format="currency"
                    />
                  </div>

                  {/* ── Charts ── */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <Card className="p-6">
                      <h2 className="text-lg font-semibold mb-4">Monthly Spending Trend</h2>
                      {trend.data?.data?.length ? (
                        <TrendChart data={trend.data.data} />
                      ) : (
                        <p className="text-slate-500 text-sm">No trend data yet.</p>
                      )}
                    </Card>

                    <Card className="p-6">
                      <h2 className="text-lg font-semibold mb-4">Spending by Category</h2>
                      {categories.data?.categories?.length ? (
                        <CategoryChart
                          data={categories.data.categories.map((c) => ({
                            name: c.category,
                            value: c.total_spent,
                          }))}
                        />
                      ) : (
                        <p className="text-slate-500 text-sm">No category data yet.</p>
                      )}
                    </Card>
                  </div>

                  {/* ── Health Score + Recent Transactions ── */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {health.data && <HealthScoreCard data={health.data} />}

                    <RecentTransactions
                      transactions={summary.data.recent_transactions ?? []}
                    />
                  </div>
                </>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
