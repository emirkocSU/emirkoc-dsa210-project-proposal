import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

interface User {
  id: string;
  email: string;
  name: string;
  telegramId?: string;
  subscriptionActive: boolean;
  subscriptionExpiresAt?: string;
  createdAt: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, name: string) => Promise<boolean>;
  logout: () => Promise<void>;
  linkTelegram: (telegramId: string) => Promise<boolean>;
  updateSubscription: (active: boolean, expiresAt?: string) => void;
  clearError: () => void;
  initializeAuth: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

// Storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_data';

// API base URL
const API_BASE_URL = 'https://your-domain.com/api';

export const useAuthStore = create<AuthStore>((set, get) => ({
  // Initial state
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  // Actions
  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Login failed');
      }

      // Store token securely
      await SecureStore.setItemAsync(TOKEN_KEY, data.token);
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(data.user));

      set({
        user: data.user,
        token: data.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      set({
        isLoading: false,
        error: errorMessage,
      });
      return false;
    }
  },

  register: async (email: string, password: string, name: string) => {
    set({ isLoading: true, error: null });

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Registration failed');
      }

      // Store token securely
      await SecureStore.setItemAsync(TOKEN_KEY, data.token);
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(data.user));

      set({
        user: data.user,
        token: data.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      set({
        isLoading: false,
        error: errorMessage,
      });
      return false;
    }
  },

  logout: async () => {
    set({ isLoading: true });

    try {
      // Call logout API if needed
      const { token } = get();
      if (token) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.warn('Logout API call failed:', error);
    }

    // Clear stored data
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await AsyncStorage.removeItem(USER_KEY);

    set({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  },

  linkTelegram: async (telegramId: string) => {
    const { token } = get();
    if (!token) return false;

    set({ isLoading: true, error: null });

    try {
      const response = await fetch(`${API_BASE_URL}/auth/link-telegram`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ telegramId }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Telegram linking failed');
      }

      // Update user data
      const updatedUser = { ...get().user!, telegramId };
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(updatedUser));

      set({
        user: updatedUser,
        isLoading: false,
        error: null,
      });

      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Telegram linking failed';
      set({
        isLoading: false,
        error: errorMessage,
      });
      return false;
    }
  },

  updateSubscription: (active: boolean, expiresAt?: string) => {
    const { user } = get();
    if (!user) return;

    const updatedUser = {
      ...user,
      subscriptionActive: active,
      subscriptionExpiresAt: expiresAt,
    };

    // Update stored user data
    AsyncStorage.setItem(USER_KEY, JSON.stringify(updatedUser));

    set({ user: updatedUser });
  },

  clearError: () => {
    set({ error: null });
  },

  initializeAuth: async () => {
    set({ isLoading: true });

    try {
      // Get stored token and user data
      const token = await SecureStore.getItemAsync(TOKEN_KEY);
      const userJson = await AsyncStorage.getItem(USER_KEY);

      if (token && userJson) {
        const user = JSON.parse(userJson);

        // Verify token with server
        const response = await fetch(`${API_BASE_URL}/auth/verify`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          
          set({
            user: data.user || user,
            token,
            isAuthenticated: true,
            isLoading: false,
          });
        } else {
          // Token is invalid, clear stored data
          await SecureStore.deleteItemAsync(TOKEN_KEY);
          await AsyncStorage.removeItem(USER_KEY);
          
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      } else {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    } catch (error) {
      console.warn('Auth initialization failed:', error);
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },
}));

// Helper functions
export const getAuthToken = async (): Promise<string | null> => {
  return await SecureStore.getItemAsync(TOKEN_KEY);
};

export const getStoredUser = async (): Promise<User | null> => {
  const userJson = await AsyncStorage.getItem(USER_KEY);
  return userJson ? JSON.parse(userJson) : null;
};

// API helper with authentication
export const authenticatedFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = await getAuthToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return fetch(url, {
    ...options,
    headers,
  });
};