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
  _hasHydrated: boolean;           // true once persist has read localStorage
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
  _setHasHydrated: (v: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      _hasHydrated: false,

      setToken: (token) => {
        set({ token, isAuthenticated: !!token });
      },

      setUser: (user) => set({ user }),

      logout: () => {
        set({ token: null, user: null, isAuthenticated: false });
      },

      _setHasHydrated: (v) => set({ _hasHydrated: v }),
    }),
    {
      name: 'auth_token',
      // Only persist meaningful data — not internal flags or functions
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // Called after Zustand finishes reading localStorage
        if (state) {
          state._setHasHydrated(true);
          // Keep api.ts interceptor in sync with the restored token
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
const current = useAuthStore.getState();
setAuthStore({
  token: current.token,
  logout: current.logout,
});

// Keep api.ts in sync whenever auth state changes
useAuthStore.subscribe((state) => {
  setAuthStore({
    token: state.token,
    logout: state.logout,
  });
});
