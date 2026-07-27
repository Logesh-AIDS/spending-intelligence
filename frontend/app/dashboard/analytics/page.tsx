'use client';

import { useState } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { CategoryChart } from '@/components/dashboard/CategoryChart';
import { TrendChart } from '@/components/dashboard/TrendChart';
import {
  useMerchantAnalytics,
  useIncomeVsExpense,
  useSpendingBehaviour,
  useFinancialStatistics,
  useReport,
} from '@/lib/hooks/useAnalytics';
import { useCategoryAnalytics } from '@/lib/hooks/useDashboard';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

const fmt = (v: number) => `₹${v.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-2 border-b last:border-0">
      <span className="text-sm text-slate-600">{label}</span>
      <span className="text-sm font-semibold">{value}</span>
    </div>
  );
}

export default function AnalyticsPage() {
  const [ivePeriod, setIvePeriod] = useState<'daily'|'weekly'|'monthly'|'yearly'>('monthly');
  const [reportType, setReportType] = useState<'weekly'|'monthly'|'yearly'>('monthly');

  const categories = useCategoryAnalytics();
  const merchants = useMerchantAnalytics();
  const ive = useIncomeVsExpense(ivePeriod);
  const behaviour = useSpendingBehaviour();
  const stats = useFinancialStatistics();
  const report = useReport(reportType);

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto py-8 px-4 space-y-8">

            <div>
              <h1 className="text-3xl font-bold">Analytics</h1>
              <p className="text-slate-600">Deep insights into your spending patterns</p>
            </div>

            {/* Category + Merchant */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Spending by Category</h2>
                {categories.isLoading ? <Skeleton className="h-64" /> :
                  categories.data?.categories?.length ? (
                    <CategoryChart data={categories.data.categories.map(c => ({ name: c.category, value: c.total_spent }))} />
                  ) : <p className="text-slate-500 text-sm">No data yet</p>
                }
              </Card>

              <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Top Merchants</h2>
                {merchants.isLoading ? <Skeleton className="h-64" /> :
                  merchants.data?.merchants?.length ? (
                    <ResponsiveContainer width="100%" height={280}>
                      <BarChart data={merchants.data.merchants.slice(0, 8)} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" tickFormatter={fmt} tick={{ fontSize: 11 }} />
                        <YAxis type="category" dataKey="merchant" tick={{ fontSize: 11 }} width={90} />
                        <Tooltip formatter={(v: number) => fmt(v)} />
                        <Bar dataKey="total_spent" fill="#3b82f6" name="Total Spent" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : <p className="text-slate-500 text-sm">No merchant data yet</p>
                }
                {merchants.data && (
                  <p className="text-sm text-slate-500 mt-3">
                    Favourite: <span className="font-semibold">{merchants.data.favorite_merchant || '—'}</span>
                    {' · '}{merchants.data.total_merchants} unique merchants
                  </p>
                )}
              </Card>
            </div>

            {/* Income vs Expense */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Income vs Expense</h2>
                <select
                  className="border border-slate-300 rounded-md px-3 py-1.5 text-sm bg-white"
                  value={ivePeriod}
                  onChange={(e) => setIvePeriod(e.target.value as any)}
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>
              {ive.isLoading ? <Skeleton className="h-72" /> :
                ive.data?.data?.length ? (
                  <>
                    <TrendChart data={ive.data.data.map(d => ({ label: d.label, expenses: d.expense, income: d.income }))} />
                    <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
                      <div className="text-center">
                        <p className="text-sm text-slate-500">Total Income</p>
                        <p className="text-lg font-bold text-green-600">{fmt(ive.data.total_income)}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-slate-500">Total Expense</p>
                        <p className="text-lg font-bold text-red-600">{fmt(ive.data.total_expense)}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-slate-500">Savings Rate</p>
                        <p className="text-lg font-bold">{ive.data.overall_savings_rate.toFixed(1)}%</p>
                      </div>
                    </div>
                  </>
                ) : <p className="text-slate-500 text-sm">No data yet</p>
              }
            </Card>

            {/* Behaviour + Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Spending Behaviour</h2>
                {behaviour.isLoading ? <Skeleton className="h-48" /> :
                  behaviour.data ? (
                    <div>
                      <StatRow label="Average Transaction" value={fmt(behaviour.data.average_spending)} />
                      <StatRow label="Median Transaction" value={fmt(behaviour.data.median_spending)} />
                      <StatRow label="Highest Transaction" value={fmt(behaviour.data.max_spending)} />
                      <StatRow label="Lowest Transaction" value={fmt(behaviour.data.min_spending)} />
                      <StatRow label="Std Deviation" value={fmt(behaviour.data.std_deviation)} />
                      <StatRow label="Transactions / Day" value={behaviour.data.transaction_frequency_per_day.toFixed(2)} />
                      <StatRow label="Weekend Spending" value={fmt(behaviour.data.weekend_spending)} />
                      <StatRow label="Weekday Spending" value={fmt(behaviour.data.weekday_spending)} />
                      <StatRow label="Most Active Day" value={behaviour.data.most_active_day || '—'} />
                    </div>
                  ) : <p className="text-slate-500 text-sm">No data yet</p>
                }
              </Card>

              <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Financial Statistics</h2>
                {stats.isLoading ? <Skeleton className="h-48" /> :
                  stats.data ? (
                    <div>
                      <StatRow label="Total Transactions" value={stats.data.total_transactions.toString()} />
                      <StatRow label="Total Debits" value={`${stats.data.total_debit_transactions} (${fmt(stats.data.total_debit_amount)})`} />
                      <StatRow label="Total Credits" value={`${stats.data.total_credit_transactions} (${fmt(stats.data.total_credit_amount)})`} />
                      <StatRow label="Avg Debit Amount" value={fmt(stats.data.average_debit_amount)} />
                      <StatRow label="Avg Credit Amount" value={fmt(stats.data.average_credit_amount)} />
                      <StatRow label="Highest Debit" value={stats.data.highest_debit ? fmt(stats.data.highest_debit) : '—'} />
                      <StatRow label="Highest Credit" value={stats.data.highest_credit ? fmt(stats.data.highest_credit) : '—'} />
                      <StatRow label="Std Deviation" value={fmt(stats.data.std_deviation_spending)} />
                    </div>
                  ) : <p className="text-slate-500 text-sm">No data yet</p>
                }
              </Card>
            </div>

            {/* Report */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Financial Report</h2>
                <select
                  className="border border-slate-300 rounded-md px-3 py-1.5 text-sm bg-white"
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value as any)}
                >
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>
              {report.isLoading ? <Skeleton className="h-40" /> :
                report.data?.entries?.length ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-slate-50">
                        <tr>
                          <th className="text-left px-3 py-2 text-slate-600">Period</th>
                          <th className="text-right px-3 py-2 text-slate-600">Income</th>
                          <th className="text-right px-3 py-2 text-slate-600">Expense</th>
                          <th className="text-right px-3 py-2 text-slate-600">Savings</th>
                          <th className="text-left px-3 py-2 text-slate-600">Top Merchant</th>
                          <th className="text-center px-3 py-2 text-slate-600">Txns</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {report.data.entries.map((e) => (
                          <tr key={e.label} className="hover:bg-slate-50">
                            <td className="px-3 py-2 font-medium">{e.label}</td>
                            <td className="px-3 py-2 text-right text-green-600">{fmt(e.income)}</td>
                            <td className="px-3 py-2 text-right text-red-600">{fmt(e.expense)}</td>
                            <td className={`px-3 py-2 text-right font-semibold ${e.savings >= 0 ? 'text-green-600' : 'text-red-600'}`}>{fmt(e.savings)}</td>
                            <td className="px-3 py-2 text-slate-600">{e.top_merchant || '—'}</td>
                            <td className="px-3 py-2 text-center text-slate-600">{e.transaction_count}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : <p className="text-slate-500 text-sm">No report data yet</p>
              }
            </Card>

          </div>
        </main>
      </div>
    </div>
  );
}
