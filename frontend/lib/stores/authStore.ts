import { create } from 'zustand';
import { setAuthStore } from '@/lib/api';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  setIsLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => {
  const store = {
    token: null,
    user: null,
    isLoading: false,
    isAuthenticated: false,
    setToken: (token: string | null) => {
      set({ token, isAuthenticated: !!token });
      // Persist to localStorage
      if (typeof window !== 'undefined') {
        if (token) {
          localStorage.setItem('auth_token', token);
        } else {
          localStorage.removeItem('auth_token');
        }
      }
    },
    setUser: (user: User | null) => set({ user }),
    setIsLoading: (isLoading: boolean) => set({ isLoading }),
    logout: () => {
      set({ token: null, user: null, isAuthenticated: false });
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
      }
    },
  };

  // Initialize from localStorage
  if (typeof window !== 'undefined') {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      store.setToken(storedToken);
    }
  }

  // Register with API client
  setAuthStore(store);

  return store;
});
