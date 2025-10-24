/**
 * Authentication Store
 * Manages user authentication state using Zustand
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import * as api from '@/services/apiClient';

interface AuthState {
  isAuthenticated: boolean;
  userEmail: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, internal_domain: string, timezone?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    (set) => ({
      isAuthenticated: api.isAuthenticated(),
      userEmail: api.getUserEmail(),
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          await api.login(email, password);
          set({
            isAuthenticated: true,
            userEmail: email,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.message || 'Login failed',
            isLoading: false,
          });
          throw error;
        }
      },

      signup: async (email: string, password: string, internal_domain: string, timezone?: string) => {
        set({ isLoading: true, error: null });
        try {
          await api.createUser({ email, password, internal_domain, timezone });
          set({ isLoading: false });
        } catch (error: any) {
          set({
            error: error.message || 'Signup failed',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        api.logout();
        set({
          isAuthenticated: false,
          userEmail: null,
          error: null,
        });
      },

      checkAuth: () => {
        const isAuth = api.isAuthenticated();
        const email = api.getUserEmail();
        set({
          isAuthenticated: isAuth,
          userEmail: email,
        });
      },

      clearError: () => set({ error: null }),
    }),
    { name: 'AuthStore' }
  )
);
