/**
 * Authentication Service with React Context
 * Handles user authentication, secure storage, and API communication
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import * as SecureStore from 'expo-secure-store';
import axios from 'axios';
import Constants from 'expo-constants';

// API Configuration
const API_BASE_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000';

// Secure storage keys
const STORAGE_KEYS = {
  USER_TOKEN: 'user_token',
  USER_DATA: 'user_data',
  REFRESH_TOKEN: 'refresh_token',
};

// Create authentication context
const AuthContext = createContext({
  user: null,
  isLoading: true,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  refreshUser: async () => {},
});

// API client with interceptors
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await SecureStore.getItemAsync(STORAGE_KEYS.USER_TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, try to refresh or logout
      await SecureStore.deleteItemAsync(STORAGE_KEYS.USER_TOKEN);
      await SecureStore.deleteItemAsync(STORAGE_KEYS.USER_DATA);
    }
    return Promise.reject(error);
  }
);

// Authentication Provider Component
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize authentication state
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setIsLoading(true);
      
      // Try to get stored user data
      const [storedToken, storedUserData] = await Promise.all([
        SecureStore.getItemAsync(STORAGE_KEYS.USER_TOKEN),
        SecureStore.getItemAsync(STORAGE_KEYS.USER_DATA),
      ]);

      if (storedToken && storedUserData) {
        const userData = JSON.parse(storedUserData);
        setUser(userData);
        
        // Verify token is still valid
        try {
          await apiClient.get('/api/auth/verify');
        } catch (error) {
          console.log('Token verification failed, clearing stored auth');
          await clearStoredAuth();
          setUser(null);
        }
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
      await clearStoredAuth();
    } finally {
      setIsLoading(false);
    }
  };

  const clearStoredAuth = async () => {
    try {
      await Promise.all([
        SecureStore.deleteItemAsync(STORAGE_KEYS.USER_TOKEN),
        SecureStore.deleteItemAsync(STORAGE_KEYS.USER_DATA),
        SecureStore.deleteItemAsync(STORAGE_KEYS.REFRESH_TOKEN),
      ]);
    } catch (error) {
      console.error('Error clearing stored auth:', error);
    }
  };

  const login = useCallback(async (email, password) => {
    try {
      setIsLoading(true);

      // For MVP, we'll simulate API call since backend might not be fully implemented
      // In production, this would be a real API call
      const mockResponse = {
        data: {
          user: {
            id: Date.now(),
            email: email,
            fullName: email.split('@')[0],
            createdAt: new Date().toISOString(),
            isLinked: false,
            telegramId: null,
          },
          token: `mock_token_${Date.now()}`,
        }
      };

      // Store authentication data
      await Promise.all([
        SecureStore.setItemAsync(STORAGE_KEYS.USER_TOKEN, mockResponse.data.token),
        SecureStore.setItemAsync(STORAGE_KEYS.USER_DATA, JSON.stringify(mockResponse.data.user)),
      ]);

      setUser(mockResponse.data.user);
      return { success: true, user: mockResponse.data.user };

    } catch (error) {
      console.error('Login error:', error);
      
      let errorMessage = 'Login failed. Please try again.';
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (email, password, fullName) => {
    try {
      setIsLoading(true);

      // Validate input
      if (!email || !password || !fullName) {
        throw new Error('All fields are required');
      }

      if (password.length < 6) {
        throw new Error('Password must be at least 6 characters');
      }

      // For MVP, simulate registration
      const mockResponse = {
        data: {
          user: {
            id: Date.now(),
            email: email,
            fullName: fullName,
            createdAt: new Date().toISOString(),
            isLinked: false,
            telegramId: null,
          },
          token: `mock_token_${Date.now()}`,
        }
      };

      // Store authentication data
      await Promise.all([
        SecureStore.setItemAsync(STORAGE_KEYS.USER_TOKEN, mockResponse.data.token),
        SecureStore.setItemAsync(STORAGE_KEYS.USER_DATA, JSON.stringify(mockResponse.data.user)),
      ]);

      setUser(mockResponse.data.user);
      return { success: true, user: mockResponse.data.user };

    } catch (error) {
      console.error('Registration error:', error);
      
      let errorMessage = 'Registration failed. Please try again.';
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Clear stored authentication data
      await clearStoredAuth();
      
      // Clear user state
      setUser(null);
      
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false, error: 'Logout failed' };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      if (!user) return { success: false, error: 'No user to refresh' };

      // For MVP, just return current user
      // In production, this would fetch updated user data from API
      const storedUserData = await SecureStore.getItemAsync(STORAGE_KEYS.USER_DATA);
      if (storedUserData) {
        const userData = JSON.parse(storedUserData);
        setUser(userData);
        return { success: true, user: userData };
      }
      
      return { success: false, error: 'No stored user data' };
    } catch (error) {
      console.error('Refresh user error:', error);
      return { success: false, error: 'Failed to refresh user data' };
    }
  }, [user]);

  const updateUser = useCallback(async (updates) => {
    try {
      if (!user) return { success: false, error: 'No user to update' };

      const updatedUser = { ...user, ...updates };
      
      // Store updated user data
      await SecureStore.setItemAsync(STORAGE_KEYS.USER_DATA, JSON.stringify(updatedUser));
      
      setUser(updatedUser);
      return { success: true, user: updatedUser };
    } catch (error) {
      console.error('Update user error:', error);
      return { success: false, error: 'Failed to update user data' };
    }
  }, [user]);

  const contextValue = {
    user,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
    updateUser,
    apiClient,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use authentication context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Utility functions for external use
export const authUtils = {
  // Check if user is authenticated
  isAuthenticated: (user) => !!user,
  
  // Check if user has linked Telegram
  isLinkedToTelegram: (user) => !!user?.telegramId,
  
  // Get user display name
  getUserDisplayName: (user) => user?.fullName || user?.email?.split('@')[0] || 'User',
  
  // Format user creation date
  formatUserDate: (user) => {
    if (!user?.createdAt) return 'Unknown';
    return new Date(user.createdAt).toLocaleDateString();
  },
  
  // Validate email format
  isValidEmail: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },
  
  // Validate password strength
  isValidPassword: (password) => {
    return password && password.length >= 6;
  },
};

// Export API client for use in other services
export { apiClient };