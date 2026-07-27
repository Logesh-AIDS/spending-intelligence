import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';

// ── Merchant Analytics ───────────────────────────────────────────

export interface MerchantStat {
  merchant: string;
  total_spent: number;
  transaction_count: number;
  percentage: number;
  average_amount: number;
}

export interface MerchantAnalytics {
  total_merchants: number;
  favorite_merchant: string | null;
  merchants: MerchantStat[];
}

export const useMerchantAnalytics = () =>
  useQuery<MerchantAnalytics>({
    queryKey: ['merchantAnalytics'],
    queryFn: async () => (await apiClient.get('/analytics/merchants')).data,
    staleTime: 5 * 60 * 1000,
  });

// ── Income vs Expense ────────────────────────────────────────────

export interface IncomeExpensePoint {
  label: string;
  income: number;
  expense: number;
  savings: number;
  savings_rate: number;
}

export interface IncomeVsExpense {
  period: string;
  total_income: number;
  total_expense: number;
  total_savings: number;
  overall_savings_rate: number;
  data: IncomeExpensePoint[];
}

export const useIncomeVsExpense = (period: 'daily' | 'weekly' | 'monthly' | 'yearly' = 'monthly') =>
  useQuery<IncomeVsExpense>({
    queryKey: ['incomeVsExpense', period],
    queryFn: async () =>
      (await apiClient.get('/analytics/income-vs-expense', { params: { period } })).data,
    staleTime: 5 * 60 * 1000,
  });

// ── Spending Behaviour ───────────────────────────────────────────

export interface SpendingBehaviour {
  average_spending: number;
  median_spending: number;
  max_spending: number;
  min_spending: number;
  std_deviation: number;
  transaction_frequency_per_day: number;
  weekend_spending: number;
  weekday_spending: number;
  weekend_vs_weekday_ratio: number;
  most_active_day: string | null;
}

export const useSpendingBehaviour = () =>
  useQuery<SpendingBehaviour>({
    queryKey: ['spendingBehaviour'],
    queryFn: async () => (await apiClient.get('/analytics/behaviour')).data,
    staleTime: 5 * 60 * 1000,
  });

// ── Financial Statistics ─────────────────────────────────────────

export interface FinancialStatistics {
  total_transactions: number;
  total_debit_transactions: number;
  total_credit_transactions: number;
  total_debit_amount: number;
  total_credit_amount: number;
  average_debit_amount: number;
  average_credit_amount: number;
  highest_debit: number | null;
  highest_credit: number | null;
  lowest_debit: number | null;
  lowest_credit: number | null;
  std_deviation_spending: number;
}

export const useFinancialStatistics = () =>
  useQuery<FinancialStatistics>({
    queryKey: ['financialStatistics'],
    queryFn: async () => (await apiClient.get('/analytics/statistics')).data,
    staleTime: 5 * 60 * 1000,
  });

// ── Report ───────────────────────────────────────────────────────

export interface ReportEntry {
  label: string;
  income: number;
  expense: number;
  savings: number;
  transaction_count: number;
  top_merchant: string | null;
  top_category: string | null;
}

export interface Report {
  report_type: string;
  generated_at: string;
  total_income: number;
  total_expense: number;
  total_savings: number;
  entries: ReportEntry[];
}

export const useReport = (report_type: 'weekly' | 'monthly' | 'yearly' = 'monthly') =>
  useQuery<Report>({
    queryKey: ['report', report_type],
    queryFn: async () =>
      (await apiClient.get('/analytics/report', { params: { report_type } })).data,
    staleTime: 5 * 60 * 1000,
  });
