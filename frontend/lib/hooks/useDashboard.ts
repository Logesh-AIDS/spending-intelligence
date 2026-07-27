import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';

// ── Types matching backend response schemas ──────────────────────

export interface RecentTransaction {
  id: number;
  bank: string;
  transaction_type: 'Debit' | 'Credit';
  amount: number;
  merchant: string | null;
  date: string;
  category: string;
}

export interface DashboardSummary {
  current_balance: number | null;
  total_spending: number;
  total_income: number;
  net_cash_flow: number;
  savings_percentage: number;
  today_spending: number;
  this_week_spending: number;
  this_month_spending: number;
  this_year_spending: number;
  total_transactions: number;
  debit_count: number;
  credit_count: number;
  highest_expense: number | null;
  highest_income: number | null;
  average_transaction: number | null;
  average_daily_spending: number;
  recent_transactions: RecentTransaction[];
}

export interface TrendPoint {
  label: string;
  amount: number;
  count: number;
}

export interface SpendingTrend {
  period: string;
  data: TrendPoint[];
}

export interface CategoryStat {
  category: string;
  total_spent: number;
  transaction_count: number;
  percentage: number;
}

export interface CategoryAnalytics {
  total_categories: number;
  highest_spending_category: string | null;
  categories: CategoryStat[];
}

export interface HealthScore {
  score: number;
  grade: string;
  savings_component: number;
  expense_component: number;
  consistency_component: number;
  cash_flow_component: number;
  trend_component: number;
  interpretation: string;
  improvement_tips: string[];
  calculated_at: string;
}

// ── Hooks ────────────────────────────────────────────────────────

export const useDashboardSummary = () => {
  return useQuery<DashboardSummary>({
    queryKey: ['dashboardSummary'],
    queryFn: async () => {
      const res = await apiClient.get<DashboardSummary>('/dashboard/summary');
      return res.data;
    },
    staleTime: 2 * 60 * 1000,   // 2 minutes
  });
};

export const useSpendingTrend = (period: 'daily' | 'weekly' | 'monthly' | 'yearly' = 'monthly') => {
  return useQuery<SpendingTrend>({
    queryKey: ['spendingTrend', period],
    queryFn: async () => {
      const res = await apiClient.get<SpendingTrend>('/dashboard/spending-trend', {
        params: { period },
      });
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};

export const useCategoryAnalytics = () => {
  return useQuery<CategoryAnalytics>({
    queryKey: ['categoryAnalytics'],
    queryFn: async () => {
      const res = await apiClient.get<CategoryAnalytics>('/analytics/categories');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};

export const useHealthScore = () => {
  return useQuery<HealthScore>({
    queryKey: ['healthScore'],
    queryFn: async () => {
      const res = await apiClient.get<HealthScore>('/health-score');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};
