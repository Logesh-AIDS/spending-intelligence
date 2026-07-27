import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';

// ── Types matching backend TransactionResponse schema ────────────

export interface Transaction {
  id: number;
  bank: string;
  account_number: string | null;
  transaction_type: 'Debit' | 'Credit';
  amount: number;
  date: string;           // DD/MM/YY
  merchant: string | null;
  upi_reference: string | null;
  balance: number | null;
  category: string;
  created_at: string;
}

export interface PaginatedTransactions {
  total_records: number;
  current_page: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
  transactions: Transaction[];
}

export interface TransactionFilters {
  page?: number;
  page_size?: number;
  transaction_type?: 'Debit' | 'Credit';
  merchant?: string;
  bank?: string;
  category?: string;
  date_from?: string;
  date_to?: string;
  min_amount?: number;
  max_amount?: number;
  search?: string;
  sort_by?: 'date' | 'amount' | 'merchant' | 'created_at';
  sort_order?: 'asc' | 'desc';
}

export interface TransactionCreate {
  bank: string;
  account_number?: string;
  transaction_type: 'Debit' | 'Credit';
  amount: number;
  date: string;
  merchant?: string;
  upi_reference?: string;
  balance?: number;
  category?: string;
}

// ── Hooks ────────────────────────────────────────────────────────

export const useTransactions = (filters?: TransactionFilters) => {
  return useQuery<PaginatedTransactions>({
    queryKey: ['transactions', filters],
    queryFn: async () => {
      const response = await apiClient.get<PaginatedTransactions>('/transactions/', {
        params: filters,
      });
      return response.data;
    },
    staleTime: 60 * 1000,
    placeholderData: (prev) => prev,  // keep showing old data while fetching next page
  });
};

export const useCreateTransaction = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: TransactionCreate) => {
      const response = await apiClient.post<Transaction>('/transactions/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
    },
  });
};

export const useUpdateTransaction = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<TransactionCreate> }) => {
      const response = await apiClient.put<Transaction>(`/transactions/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
    },
  });
};

export const useDeleteTransaction = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/transactions/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
    },
  });
};

export const useSendSMS = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (raw_sms: string) => {
      const response = await apiClient.post('/sms/', { raw_sms });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
    },
  });
};
