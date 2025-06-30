/**
 * Telegram Linking Service
 * Handles deep link generation, token management, and Telegram integration
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import * as Linking from 'expo-linking';
import Constants from 'expo-constants';
import { v4 as uuidv4 } from 'uuid';
import { useAuth } from './authService';

// Configuration
const BOT_USERNAME = Constants.expoConfig?.extra?.botUsername || 'YourBotUsername';
const API_BASE_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000';

// Create linking context
const LinkingContext = createContext({
  isLinking: false,
  linkingStatus: null,
  generateTelegramLink: async () => {},
  checkLinkingStatus: async () => {},
  clearLinkingStatus: () => {},
});

// Linking Provider Component
export function LinkingProvider({ children }) {
  const [isLinking, setIsLinking] = useState(false);
  const [linkingStatus, setLinkingStatus] = useState(null);
  const { user, updateUser, apiClient } = useAuth();

  const generateTelegramLink = useCallback(async () => {
    try {
      if (!user) {
        throw new Error('User must be logged in to generate Telegram link');
      }

      setIsLinking(true);
      setLinkingStatus(null);

      // Generate unique linking token
      const linkingToken = generateLinkingToken(user.id);
      
      // For MVP, we'll store the token locally and simulate API call
      // In production, this would send the token to the backend
      console.log('Generated linking token:', linkingToken);
      
      // Create Telegram deep link
      const telegramLink = createTelegramDeepLink(linkingToken);
      
      // Open Telegram with the deep link
      const canOpen = await Linking.canOpenURL(telegramLink);
      if (canOpen) {
        await Linking.openURL(telegramLink);
        
        setLinkingStatus({
          status: 'pending',
          message: 'Telegram opened. Please start the bot to complete linking.',
          token: linkingToken,
          timestamp: new Date().toISOString(),
        });
        
        // Start polling for linking completion
        startLinkingStatusPolling(linkingToken);
        
        return { success: true, link: telegramLink, token: linkingToken };
      } else {
        throw new Error('Unable to open Telegram. Please install Telegram app.');
      }
    } catch (error) {
      console.error('Error generating Telegram link:', error);
      setLinkingStatus({
        status: 'error',
        message: error.message || 'Failed to generate Telegram link',
        timestamp: new Date().toISOString(),
      });
      return { success: false, error: error.message };
    } finally {
      setIsLinking(false);
    }
  }, [user, updateUser]);

  const checkLinkingStatus = useCallback(async (token) => {
    try {
      if (!token) return { success: false, error: 'No token provided' };

      // For MVP, simulate checking linking status
      // In production, this would query the backend API
      console.log('Checking linking status for token:', token);
      
      // Simulate random success/pending status for demo
      const isLinked = Math.random() > 0.7; // 30% chance of being linked
      
      if (isLinked) {
        // Simulate successful linking
        const linkedUser = {
          ...user,
          isLinked: true,
          telegramId: Math.floor(Math.random() * 1000000),
          telegramUsername: 'demo_user',
          linkedAt: new Date().toISOString(),
        };
        
        await updateUser(linkedUser);
        
        setLinkingStatus({
          status: 'success',
          message: 'Successfully linked to Telegram!',
          timestamp: new Date().toISOString(),
        });
        
        return { success: true, linked: true, user: linkedUser };
      } else {
        return { success: true, linked: false };
      }
    } catch (error) {
      console.error('Error checking linking status:', error);
      return { success: false, error: error.message };
    }
  }, [user, updateUser]);

  const startLinkingStatusPolling = useCallback((token) => {
    let pollCount = 0;
    const maxPolls = 30; // Poll for 5 minutes (30 * 10 seconds)
    
    const pollInterval = setInterval(async () => {
      pollCount++;
      
      const result = await checkLinkingStatus(token);
      
      if (result.success && result.linked) {
        // Linking successful
        clearInterval(pollInterval);
      } else if (pollCount >= maxPolls) {
        // Timeout
        clearInterval(pollInterval);
        setLinkingStatus({
          status: 'timeout',
          message: 'Linking timeout. Please try again.',
          timestamp: new Date().toISOString(),
        });
      }
    }, 10000); // Poll every 10 seconds
    
    // Store interval ID for cleanup
    return pollInterval;
  }, [checkLinkingStatus]);

  const clearLinkingStatus = useCallback(() => {
    setLinkingStatus(null);
  }, []);

  const unlinkTelegram = useCallback(async () => {
    try {
      if (!user?.isLinked) {
        throw new Error('No Telegram account linked');
      }

      setIsLinking(true);

      // For MVP, simulate unlinking
      const unlinkedUser = {
        ...user,
        isLinked: false,
        telegramId: null,
        telegramUsername: null,
        linkedAt: null,
      };

      await updateUser(unlinkedUser);

      setLinkingStatus({
        status: 'unlinked',
        message: 'Successfully unlinked from Telegram',
        timestamp: new Date().toISOString(),
      });

      return { success: true, user: unlinkedUser };
    } catch (error) {
      console.error('Error unlinking Telegram:', error);
      setLinkingStatus({
        status: 'error',
        message: error.message || 'Failed to unlink Telegram',
        timestamp: new Date().toISOString(),
      });
      return { success: false, error: error.message };
    } finally {
      setIsLinking(false);
    }
  }, [user, updateUser]);

  const contextValue = {
    isLinking,
    linkingStatus,
    generateTelegramLink,
    checkLinkingStatus,
    clearLinkingStatus,
    unlinkTelegram,
  };

  return (
    <LinkingContext.Provider value={contextValue}>
      {children}
    </LinkingContext.Provider>
  );
}

// Hook to use linking context
export function useLinking() {
  const context = useContext(LinkingContext);
  if (!context) {
    throw new Error('useLinking must be used within a LinkingProvider');
  }
  return context;
}

// Utility functions

/**
 * Generate a secure linking token
 */
function generateLinkingToken(userId) {
  const timestamp = Date.now();
  const randomId = uuidv4();
  const payload = `${userId}_${timestamp}_${randomId}`;
  
  // For MVP, use base64 encoding. In production, use proper encryption
  return btoa(payload).replace(/[+/=]/g, '').substring(0, 32);
}

/**
 * Create Telegram deep link with token
 */
function createTelegramDeepLink(token) {
  const botUsername = BOT_USERNAME.startsWith('@') ? BOT_USERNAME.slice(1) : BOT_USERNAME;
  return `https://t.me/${botUsername}?start=${token}`;
}

/**
 * Parse linking token to extract information
 */
function parseLinkingToken(token) {
  try {
    // Add padding if needed for base64 decoding
    const paddedToken = token + '=='.slice(0, (4 - token.length % 4) % 4);
    const decoded = atob(paddedToken);
    const [userId, timestamp, randomId] = decoded.split('_');
    
    return {
      userId: parseInt(userId),
      timestamp: parseInt(timestamp),
      randomId,
      isExpired: Date.now() - parseInt(timestamp) > 24 * 60 * 60 * 1000, // 24 hours
    };
  } catch (error) {
    console.error('Error parsing linking token:', error);
    return null;
  }
}

/**
 * Validate linking token
 */
function validateLinkingToken(token, userId) {
  const parsed = parseLinkingToken(token);
  if (!parsed) return false;
  
  return parsed.userId === userId && !parsed.isExpired;
}

// Export utility functions
export const linkingUtils = {
  generateLinkingToken,
  createTelegramDeepLink,
  parseLinkingToken,
  validateLinkingToken,
  
  // Get linking status display info
  getLinkingStatusInfo: (status) => {
    const statusMap = {
      pending: {
        icon: '⏳',
        color: '#f59e0b',
        title: 'Linking in Progress',
      },
      success: {
        icon: '✅',
        color: '#10b981',
        title: 'Successfully Linked',
      },
      error: {
        icon: '❌',
        color: '#ef4444',
        title: 'Linking Failed',
      },
      timeout: {
        icon: '⏱️',
        color: '#f59e0b',
        title: 'Linking Timeout',
      },
      unlinked: {
        icon: '🔓',
        color: '#6b7280',
        title: 'Unlinked',
      },
    };
    
    return statusMap[status] || {
      icon: '❓',
      color: '#6b7280',
      title: 'Unknown Status',
    };
  },
  
  // Check if user can generate new link
  canGenerateNewLink: (user, linkingStatus) => {
    if (!user) return false;
    if (user.isLinked) return false;
    if (linkingStatus?.status === 'pending') return false;
    return true;
  },
  
  // Format Telegram username for display
  formatTelegramUsername: (username) => {
    if (!username) return 'Unknown';
    return username.startsWith('@') ? username : `@${username}`;
  },
};