import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { setAuthStore } from '@/lib/api';

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      setToken: (token) => {
        set({ token, isAuthenticated: !!token });
      },

      setUser: (user) => set({ user }),

      logout: () => {
        set({ token: null, user: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth_token',          // localStorage key
      partialize: (state) => ({    // only persist token and user — not functions
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // After Zustand rehydrates from localStorage, register with api.ts
        if (state) {
          setAuthStore({
            token: state.token,
            logout: state.logout,
          });
        }
      },
    }
  )
);

// Register initial state with api.ts on first load
// (onRehydrateStorage handles refresh; this handles first login)
const current = useAuthStore.getState();
setAuthStore({
  token: current.token,
  logout: current.logout,
});

// Keep api.ts in sync whenever the store changes
useAuthStore.subscribe((state) => {
  setAuthStore({
    token: state.token,
    logout: state.logout,
  });
});
