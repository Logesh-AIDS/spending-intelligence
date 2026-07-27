import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';

export interface Goal {
  id: number;
  title: string;
  goal_type: 'save' | 'limit_category' | 'limit_spending' | 'emergency_fund';
  target_amount: number;
  current_amount: number;
  category: string | null;
  deadline: string | null;
  is_active: boolean;
  is_achieved: boolean;
  progress_percentage: number;
  ai_prediction: string | null;
  created_at: string;
}

export interface GoalCreate {
  title: string;
  goal_type: 'save' | 'limit_category' | 'limit_spending' | 'emergency_fund';
  target_amount: number;
  category?: string;
  deadline?: string;
}

export const useGoals = () =>
  useQuery<Goal[]>({
    queryKey: ['goals'],
    queryFn: async () => (await apiClient.get('/goals')).data,
    staleTime: 2 * 60 * 1000,
  });

export const useCreateGoal = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: GoalCreate) =>
      (await apiClient.post<Goal>('/goals', data)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['goals'] }),
  });
};

export const useEvaluateGoal = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) =>
      (await apiClient.get<Goal>(`/goals/${id}/evaluate`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['goals'] }),
  });
};

export const useDeleteGoal = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => apiClient.delete(`/goals/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['goals'] }),
  });
};
