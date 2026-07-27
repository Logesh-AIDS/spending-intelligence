import { useQuery, useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { useAuthStore, type User } from '@/lib/stores/authStore';

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  token: string;
  user: User;
}

interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export const useLogin = () => {
  const { setToken, setUser } = useAuthStore();

  return useMutation({
    mutationFn: async (data: LoginRequest) => {
      const response = await apiClient.post<LoginResponse>('/auth/login', data);
      return response.data;
    },
    onSuccess: (data) => {
      setToken(data.token);
      setUser(data.user);
    },
  });
};

export const useRegister = () => {
  const { setToken, setUser } = useAuthStore();

  return useMutation({
    mutationFn: async (data: RegisterRequest) => {
      const response = await apiClient.post<LoginResponse>('/auth/register', data);
      return response.data;
    },
    onSuccess: (data) => {
      setToken(data.token);
      setUser(data.user);
    },
  });
};

export const useCurrentUser = () => {
  const { user, token } = useAuthStore();

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await apiClient.get<User>('/auth/me');
      return response.data;
    },
    enabled: !!token && !user,
  });
};
