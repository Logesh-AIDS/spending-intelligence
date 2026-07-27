import { useQuery, useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { useAuthStore, type User } from '@/lib/stores/authStore';

// ── Register ────────────────────────────────────────────────────

interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;   // backend field name
}

// Backend POST /auth/register returns the created user (no token)
// We need to follow up with a login call
export const useRegister = () => {
  const { setToken, setUser } = useAuthStore();

  return useMutation({
    mutationFn: async (data: RegisterRequest) => {
      // Step 1: Create account
      await apiClient.post<User>('/auth/register', data);

      // Step 2: Login immediately to get the token
      const loginRes = await apiClient.post<{ access_token: string; token_type: string }>(
        '/auth/login',
        { email: data.email, password: data.password }
      );

      // Step 3: Fetch user profile
      const token = loginRes.data.access_token;
      const meRes = await apiClient.get<User>('/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      });

      return { token, user: meRes.data };
    },
    onSuccess: ({ token, user }) => {
      setToken(token);
      setUser(user);
    },
  });
};

// ── Login ───────────────────────────────────────────────────────

interface LoginRequest {
  email: string;
  password: string;
}

// Backend POST /auth/login returns {access_token, token_type} — no user object
export const useLogin = () => {
  const { setToken, setUser } = useAuthStore();

  return useMutation({
    mutationFn: async (data: LoginRequest) => {
      // Step 1: Get token
      const loginRes = await apiClient.post<{ access_token: string; token_type: string }>(
        '/auth/login',
        data
      );
      const token = loginRes.data.access_token;

      // Step 2: Fetch user profile with the new token
      const meRes = await apiClient.get<User>('/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      });

      return { token, user: meRes.data };
    },
    onSuccess: ({ token, user }) => {
      setToken(token);
      setUser(user);
    },
  });
};

// ── Current User ────────────────────────────────────────────────

// Used on page load to rehydrate user from stored token
export const useCurrentUser = () => {
  const { token, user, setUser } = useAuthStore();

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await apiClient.get<User>('/auth/me');
      setUser(response.data);
      return response.data;
    },
    // Only fetch if we have a token but no user loaded yet (page refresh scenario)
    enabled: !!token && !user,
    staleTime: 5 * 60 * 1000,
  });
};
