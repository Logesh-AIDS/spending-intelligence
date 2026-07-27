import { create } from 'zustand';
import { setAuthStore } from '@/lib/api';

// Matches the backend UserResponse schema
export interface User {
  id: number;
  email: string;
  full_name: string;   // backend uses full_name, not name
  is_active: boolean;
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

export const useAuthStore = create<AuthState>((set, get) => {
  const store: AuthState = {
    token: null,
    user: null,
    isLoading: false,
    isAuthenticated: false,

    setToken: (token: string | null) => {
      set({ token, isAuthenticated: !!token });
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

  // Restore token from localStorage on page load
  if (typeof window !== 'undefined') {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      store.token = storedToken;
      store.isAuthenticated = true;
    }
  }

  // Register with API client so interceptors have access to token + logout
  setAuthStore(store);

  return store;
});
