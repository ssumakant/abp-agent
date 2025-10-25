/**
 * API Client Service
 *
 * This is the ONLY module that makes HTTP requests to the backend.
 * All API calls are centralized here for consistency and maintainability.
 *
 * Features:
 * - Automatic JWT token management
 * - Request/Response interceptors
 * - Centralized error handling
 * - TypeScript type safety
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  Token,
  UserCreateRequest,
  UserCreateResponse,
  AgentResponse,
  ApprovalRequest,
  Settings,
  GoogleAuthUrlResponse,
  ConnectedAccountsResponse,
  ThreadsResponse,
  CreateThreadRequest,
  Thread,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK_API === 'true';

// Storage keys
const TOKEN_KEY = 'abp_jwt_token';
const USER_EMAIL_KEY = 'abp_user_email';

// Create axios instance
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add JWT token to all requests
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - logout user
      logout();
      window.location.href = '/';
    }

    // Format error for consistent handling
    const apiError = {
      message: error.response?.data
        ? typeof error.response.data === 'string'
          ? error.response.data
          : (error.response.data as any).detail || 'An error occurred'
        : error.message,
      status: error.response?.status,
      details: error.response?.data,
    };

    return Promise.reject(apiError);
  }
);

// ==================== TOKEN MANAGEMENT ====================

export function storeToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function storeUserEmail(email: string): void {
  localStorage.setItem(USER_EMAIL_KEY, email);
}

export function getUserEmail(): string | null {
  return localStorage.getItem(USER_EMAIL_KEY);
}

export function logout(): void {
  clearToken();
  localStorage.removeItem(USER_EMAIL_KEY);
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

// ==================== AUTHENTICATION ====================

export async function login(email: string, password: string): Promise<Token> {
  // OAuth2PasswordRequestForm expects form data
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await axiosInstance.post<Token>('/token', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  storeToken(response.data.access_token);
  storeUserEmail(email);

  return response.data;
}

export async function createUser(data: UserCreateRequest): Promise<UserCreateResponse> {
  const response = await axiosInstance.post<UserCreateResponse>('/users', data);
  return response.data;
}

// ==================== AGENT INTERACTION ====================

export async function getAgentResponse(query: string, userId?: string): Promise<AgentResponse> {
  const response = await axiosInstance.post<AgentResponse>('/agent/invoke', {
    query,
    user_id: userId,
  });
  return response.data;
}

export async function sendApproval(approvalRequest: ApprovalRequest): Promise<AgentResponse> {
  const response = await axiosInstance.post<AgentResponse>('/agent/approve', approvalRequest);
  return response.data;
}

// ==================== SETTINGS (CONSTITUTION) ====================

// Mock data for settings until backend is implemented
const mockSettings: Settings = {
  user_id: 'mock-user-id',
  work_hours: {
    start: '09:00',
    end: '17:00',
    timezone: 'America/Los_Angeles',
  },
  protected_time_blocks: [
    {
      id: 'ptb-1',
      name: 'Kids School Run',
      day_of_week: 'weekdays',
      start_time: '15:00',
      end_time: '16:00',
      recurring: true,
    },
  ],
  scheduling_rules: {
    no_weekend_meetings: true,
    busyness_threshold: 0.85,
    lookahead_days: 14,
  },
};

export async function getSettings(): Promise<Settings> {
  if (ENABLE_MOCK) {
    console.warn('Using mocked endpoint: GET /api/v1/settings');
    return new Promise((resolve) => setTimeout(() => resolve(mockSettings), 500));
  }

  try {
    const response = await axiosInstance.get<Settings>('/api/v1/settings');
    return response.data;
  } catch (error) {
    console.warn('Settings endpoint not available, using mock data');
    return mockSettings;
  }
}

export async function updateSettings(settings: Partial<Settings>): Promise<void> {
  if (ENABLE_MOCK) {
    console.warn('Using mocked endpoint: POST /api/v1/settings');
    return new Promise((resolve) => setTimeout(() => resolve(), 500));
  }

  try {
    await axiosInstance.post('/api/v1/settings', settings);
  } catch (error) {
    console.warn('Settings endpoint not available, changes not saved');
    throw error;
  }
}

// ==================== GOOGLE ACCOUNT MANAGEMENT ====================

// Mock data for connected accounts
const mockAccounts: ConnectedAccountsResponse = {
  accounts: [
    {
      account_id: 'acc-1',
      email: getUserEmail() || 'user@company.com',
      is_primary: true,
      connected_at: new Date().toISOString(),
      status: 'active',
    },
  ],
};

export async function getGoogleAuthUrl(): Promise<GoogleAuthUrlResponse> {
  if (ENABLE_MOCK) {
    console.warn('Using mocked endpoint: GET /api/v1/auth/google/url');
    return {
      auth_url: 'https://accounts.google.com/o/oauth2/v2/auth?mock=true',
    };
  }

  try {
    const response = await axiosInstance.get<GoogleAuthUrlResponse>('/api/v1/auth/google/url');
    return response.data;
  } catch (error) {
    console.warn('Google auth URL endpoint not available');
    throw new Error('Google Calendar connection is not yet available. Please check with your administrator.');
  }
}

export async function getConnectedAccounts(): Promise<ConnectedAccountsResponse> {
  if (ENABLE_MOCK) {
    console.warn('Using mocked endpoint: GET /api/v1/auth/accounts');
    return new Promise((resolve) => setTimeout(() => resolve(mockAccounts), 500));
  }

  try {
    const response = await axiosInstance.get<ConnectedAccountsResponse>('/api/v1/auth/accounts');
    return response.data;
  } catch (error) {
    console.warn('Connected accounts endpoint not available, using mock data');
    return mockAccounts;
  }
}

export async function removeConnectedAccount(accountId: string): Promise<void> {
  if (ENABLE_MOCK) {
    console.warn(`Using mocked endpoint: DELETE /api/v1/auth/accounts/${accountId}`);
    return new Promise((resolve) => setTimeout(() => resolve(), 500));
  }

  try {
    await axiosInstance.delete(`/api/v1/auth/accounts/${accountId}`);
  } catch (error) {
    console.warn('Remove account endpoint not available');
    throw error;
  }
}

// ==================== THREAD MANAGEMENT ====================

// Mock threads data
const mockThreads: Thread[] = [
  {
    thread_id: 'thread-1',
    title: 'General Conversation',
    last_message: 'Hello, how can I help you today?',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    message_count: 1,
  },
];

export async function getThreads(): Promise<ThreadsResponse> {
  if (ENABLE_MOCK) {
    console.warn('Using mocked endpoint: GET /api/v1/threads');
    return { threads: mockThreads };
  }

  try {
    const response = await axiosInstance.get<ThreadsResponse>('/api/v1/threads');
    return response.data;
  } catch (error) {
    console.warn('Threads endpoint not available, using single-thread mode');
    return { threads: [] };
  }
}

export async function createThread(data: CreateThreadRequest): Promise<Thread> {
  if (ENABLE_MOCK) {
    console.warn('Using mocked endpoint: POST /api/v1/threads');
    const newThread: Thread = {
      thread_id: `thread-${Date.now()}`,
      ...data,
      last_message: '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      message_count: 0,
    };
    return new Promise((resolve) => setTimeout(() => resolve(newThread), 500));
  }

  try {
    const response = await axiosInstance.post<Thread>('/api/v1/threads', data);
    return response.data;
  } catch (error) {
    console.warn('Create thread endpoint not available');
    throw error;
  }
}

export async function deleteThread(threadId: string): Promise<void> {
  if (ENABLE_MOCK) {
    console.warn(`Using mocked endpoint: DELETE /api/v1/threads/${threadId}`);
    return new Promise((resolve) => setTimeout(() => resolve(), 500));
  }

  try {
    await axiosInstance.delete(`/api/v1/threads/${threadId}`);
  } catch (error) {
    console.warn('Delete thread endpoint not available');
    throw error;
  }
}

export default axiosInstance;
