import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';

export interface DashboardStats {
  totalExpenses: number;
  totalIncome: number;
  balance: number;
  monthlyTrend: Array<{
    month: string;
    expenses: number;
    income: number;
  }>;
  categoryBreakdown: Array<{
    name: string;
    value: number;
  }>;
}

export const useDashboardStats = (timeframe: 'month' | 'quarter' | 'year' = 'month') => {
  return useQuery({
    queryKey: ['dashboardStats', timeframe],
    queryFn: async () => {
      const response = await apiClient.get<DashboardStats>('/dashboard/stats', {
        params: { timeframe },
      });
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
