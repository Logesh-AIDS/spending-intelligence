import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
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
  _hasHydrated: boolean;
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

      setToken: (token) => set({ token, isAuthenticated: !!token }),
      setUser: (user) => set({ user }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),
      _setHasHydrated: (v) => set({ _hasHydrated: v }),
    }),
    {
      name: 'auth_token',
      storage: createJSONStorage(() => localStorage),
      // Only persist data fields — never persist flags or functions
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state, error) => {
        // Called after Zustand finishes reading localStorage.
        // state is undefined when there is no stored data (first visit) — handle both cases.
        const store = useAuthStore.getState();
        store._setHasHydrated(true);

        if (state) {
          setAuthStore({ token: state.token, logout: store.logout });
        }
      },
    }
  )
);

// Sync api.ts interceptor whenever token changes
useAuthStore.subscribe((state) => {
  setAuthStore({ token: state.token, logout: state.logout });
});
