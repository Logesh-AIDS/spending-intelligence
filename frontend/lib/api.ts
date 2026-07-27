import axios, { AxiosInstance, AxiosError } from 'axios';

// FastAPI backend runs on port 8000
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

let authStore: { token: string | null; logout?: () => void } = { token: null };

// Called from authStore initialization so the interceptor always reads the latest token
export const setAuthStore = (store: { token: string | null; logout?: () => void }) => {
  authStore = store;
};

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — attach JWT Bearer token to every request
apiClient.interceptors.request.use(
  (config) => {
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — on 401 clear auth and redirect to /login
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      if (authStore.logout) {
        authStore.logout();
      } else {
        authStore.token = null;
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
      }
      if (typeof window !== 'undefined') {
        // /login is the correct route (not /auth/login)
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
