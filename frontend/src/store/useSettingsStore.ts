/**
 * Settings Store
 * Manages user settings/constitution using Zustand
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import * as api from '@/services/apiClient';
import type { Settings, GoogleAccount } from '@/types';

interface SettingsState {
  settings: Settings | null;
  connectedAccounts: GoogleAccount[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchSettings: () => Promise<void>;
  updateSettings: (settings: Partial<Settings>) => Promise<void>;
  fetchConnectedAccounts: () => Promise<void>;
  connectGoogleAccount: () => Promise<void>;
  removeAccount: (accountId: string) => Promise<void>;
  clearError: () => void;
}

export const useSettingsStore = create<SettingsState>()(
  devtools(
    (set) => ({
      settings: null,
      connectedAccounts: [],
      isLoading: false,
      error: null,

      fetchSettings: async () => {
        set({ isLoading: true, error: null });
        try {
          const settings = await api.getSettings();
          set({ settings, isLoading: false });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to fetch settings',
            isLoading: false,
          });
        }
      },

      updateSettings: async (updatedSettings: Partial<Settings>) => {
        set({ isLoading: true, error: null });
        try {
          await api.updateSettings(updatedSettings);
          set((state) => ({
            settings: state.settings ? { ...state.settings, ...updatedSettings } : null,
            isLoading: false,
          }));
        } catch (error: any) {
          set({
            error: error.message || 'Failed to update settings',
            isLoading: false,
          });
          throw error;
        }
      },

      fetchConnectedAccounts: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.getConnectedAccounts();
          set({ connectedAccounts: response.accounts, isLoading: false });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to fetch connected accounts',
            isLoading: false,
          });
        }
      },

      connectGoogleAccount: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.getGoogleAuthUrl();
          // Open OAuth URL in new window
          window.open(response.auth_url, '_blank', 'width=600,height=700');
          set({ isLoading: false });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to connect Google account',
            isLoading: false,
          });
          throw error;
        }
      },

      removeAccount: async (accountId: string) => {
        set({ isLoading: true, error: null });
        try {
          await api.removeConnectedAccount(accountId);
          set((state) => ({
            connectedAccounts: state.connectedAccounts.filter((acc) => acc.account_id !== accountId),
            isLoading: false,
          }));
        } catch (error: any) {
          set({
            error: error.message || 'Failed to remove account',
            isLoading: false,
          });
          throw error;
        }
      },

      clearError: () => set({ error: null }),
    }),
    { name: 'SettingsStore' }
  )
);
