# 📱 Expo Mobile App Development Guide
## Premium Car Alert Mobile App

This guide provides comprehensive instructions for developing the Premium Car Alert mobile app using Expo and React Native.

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Core Features](#core-features)
5. [API Integration](#api-integration)
6. [Authentication Flow](#authentication-flow)
7. [Push Notifications](#push-notifications)
8. [Deep Linking](#deep-linking)
9. [Building and Deployment](#building-and-deployment)
10. [Testing](#testing)

## 🎯 Project Overview

The Premium Car Alert mobile app serves as the companion app to the Telegram bot, providing:

- **User Registration & Authentication**
- **Premium Subscription Management**
- **Car Search Filter Configuration**
- **Push Notifications for Alerts**
- **Deep Linking with Telegram Bot**
- **AI Damage Detection Interface**

### Technology Stack

- **Framework**: Expo SDK 49
- **Language**: TypeScript
- **Navigation**: React Navigation 6
- **State Management**: Zustand
- **API Client**: React Query
- **Storage**: Expo SecureStore + AsyncStorage
- **Notifications**: Expo Notifications
- **Camera**: Expo Camera + Image Picker

## 🛠️ Development Setup

### 1. Prerequisites

```bash
# Install Node.js (16.x or later)
node --version

# Install Expo CLI
npm install -g @expo/cli

# Install EAS CLI for building
npm install -g eas-cli
```

### 2. Project Initialization

```bash
# Navigate to expo-app directory
cd expo-app

# Install dependencies
npm install

# Start development server
npx expo start
```

### 3. Development Tools

```bash
# Install Expo Go app on your device
# iOS: https://apps.apple.com/app/expo-go/id982107779
# Android: https://play.google.com/store/apps/details?id=host.exp.exponent

# For iOS Simulator
npx expo start --ios

# For Android Emulator
npx expo start --android

# For web development
npx expo start --web
```

## 📁 Project Structure

```
expo-app/
├── App.tsx                 # Main app component
├── app.json               # Expo configuration
├── package.json           # Dependencies
├── assets/                # Images, fonts, icons
│   ├── fonts/
│   ├── images/
│   └── icons/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── LoadingSpinner.tsx
│   ├── screens/          # Screen components
│   │   ├── WelcomeScreen.tsx
│   │   ├── LoginScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── HomeScreen.tsx
│   │   ├── FilterScreen.tsx
│   │   ├── AlertsScreen.tsx
│   │   ├── SubscriptionScreen.tsx
│   │   └── ProfileScreen.tsx
│   ├── navigation/       # Navigation configuration
│   │   ├── MainTabNavigator.tsx
│   │   └── AuthNavigator.tsx
│   ├── store/           # State management
│   │   ├── authStore.ts
│   │   ├── alertStore.ts
│   │   └── filterStore.ts
│   ├── services/        # API services
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── notifications.ts
│   ├── utils/           # Utility functions
│   │   ├── linking.ts
│   │   ├── notifications.ts
│   │   └── validation.ts
│   ├── types/           # TypeScript types
│   │   ├── api.ts
│   │   ├── navigation.ts
│   │   └── user.ts
│   └── constants/       # App constants
│       ├── colors.ts
│       ├── fonts.ts
│       └── config.ts
```

## ✨ Core Features

### 1. Authentication System

```typescript
// Features:
- Email/password registration
- Secure login with JWT tokens
- Biometric authentication (optional)
- Password recovery
- Account linking with Telegram

// Implementation:
- Zustand store for state management
- Expo SecureStore for token storage
- Form validation with proper error handling
```

### 2. Car Search Filters

```typescript
// Features:
- Car make/model selection
- Price range slider
- Year range picker
- Location/city selection
- Fuel type and transmission filters
- Real-time filter preview

// Implementation:
- Interactive UI components
- Persistent filter storage
- Sync with Telegram bot API
```

### 3. Push Notifications

```typescript
// Features:
- Real-time car listing alerts
- Subscription renewal reminders
- Promotional notifications
- Rich notification content with images

// Implementation:
- Expo Notifications API
- Background notification handling
- Deep linking from notifications
```

### 4. Premium Subscription

```typescript
// Features:
- Subscription plans display
- In-app purchase integration
- Payment processing
- Subscription status management

// Implementation:
- Stripe payment integration
- Receipt validation
- Subscription state synchronization
```

## 🔌 API Integration

### 1. API Configuration

```typescript
// src/services/api.ts
const API_BASE_URL = 'https://your-domain.com/api';

export const apiClient = {
  auth: {
    login: (credentials) => POST('/auth/login', credentials),
    register: (userData) => POST('/auth/register', userData),
    verify: () => GET('/auth/verify'),
    linkTelegram: (telegramId) => POST('/auth/link-telegram', { telegramId }),
  },
  
  filters: {
    get: () => GET('/filters'),
    update: (filters) => PUT('/filters', filters),
  },
  
  alerts: {
    getHistory: () => GET('/alerts/history'),
    markAsRead: (alertId) => POST(`/alerts/${alertId}/read`),
  },
  
  subscription: {
    getPlans: () => GET('/subscription/plans'),
    subscribe: (planId) => POST('/subscription/subscribe', { planId }),
    getStatus: () => GET('/subscription/status'),
  },
};
```

### 2. Authentication Headers

```typescript
// Automatic token injection
const authenticatedFetch = async (url: string, options: RequestInit = {}) => {
  const token = await getAuthToken();
  
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers,
    },
  });
};
```

## 🔐 Authentication Flow

### 1. Registration Process

```typescript
// Step 1: User enters email, password, name
// Step 2: API creates account and returns JWT
// Step 3: Store token securely
// Step 4: Navigate to main app
// Step 5: Optional: Link Telegram account

const register = async (email: string, password: string, name: string) => {
  const response = await apiClient.auth.register({ email, password, name });
  
  if (response.success) {
    await SecureStore.setItemAsync('auth_token', response.token);
    await AsyncStorage.setItem('user_data', JSON.stringify(response.user));
    
    // Update auth state
    setAuthState({
      user: response.user,
      token: response.token,
      isAuthenticated: true,
    });
  }
};
```

### 2. Telegram Account Linking

```typescript
// Deep link handler for Telegram bot integration
const handleTelegramLink = async (telegramId: string) => {
  const success = await linkTelegram(telegramId);
  
  if (success) {
    // Show success message
    // Enable premium features
    // Sync with Telegram bot
  }
};
```

## 🔔 Push Notifications

### 1. Setup and Permissions

```typescript
// src/utils/notifications.ts
export const setupNotifications = async () => {
  // Request permissions
  const { status } = await Notifications.requestPermissionsAsync();
  
  if (status !== 'granted') {
    throw new Error('Notification permissions not granted');
  }
  
  // Get push token
  const token = await Notifications.getExpoPushTokenAsync();
  
  // Send token to backend
  await apiClient.notifications.registerDevice(token.data);
  
  // Configure notification behavior
  Notifications.setNotificationHandler({
    handleNotification: async () => ({
      shouldShowAlert: true,
      shouldPlaySound: true,
      shouldSetBadge: true,
    }),
  });
};
```

### 2. Notification Categories

```typescript
// Car listing alerts
{
  categoryId: 'car_alert',
  title: 'New Car Found!',
  body: '2020 Toyota Corolla - $15,000 in Istanbul',
  data: {
    carId: '12345',
    listingUrl: 'https://sahibinden.com/...',
    damageScore: 25,
  },
}

// Subscription reminders
{
  categoryId: 'subscription',
  title: 'Subscription Expiring Soon',
  body: 'Your premium subscription expires in 3 days',
  data: {
    action: 'renew_subscription',
  },
}
```

## 🔗 Deep Linking

### 1. URL Scheme Configuration

```json
// app.json
{
  "expo": {
    "scheme": "premiumcaralert",
    "web": {
      "bundler": "metro"
    }
  }
}
```

### 2. Link Handling

```typescript
// src/utils/linking.ts
export const linkingConfig = {
  prefixes: ['premiumcaralert://', 'https://your-domain.com'],
  config: {
    screens: {
      // Telegram bot linking
      LinkAccount: 'link/:token',
      
      // Car details from notification
      CarDetails: 'car/:carId',
      
      // Subscription management
      Subscription: 'subscription/:action',
      
      // Filter configuration
      Filters: 'filters',
    },
  },
};
```

## 🏗️ Building and Deployment

### 1. EAS Build Configuration

```json
// eas.json
{
  "cli": {
    "version": ">= 3.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "channel": "preview"
    },
    "production": {
      "channel": "production"
    }
  },
  "submit": {
    "production": {}
  }
}
```

### 2. Build Commands

```bash
# Development build
eas build --profile development --platform ios
eas build --profile development --platform android

# Production build
eas build --profile production --platform all

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

### 3. Environment Configuration

```typescript
// src/constants/config.ts
const config = {
  development: {
    apiUrl: 'http://localhost:8000/api',
    telegramBotUrl: 'https://t.me/PremiumCarAlertDevBot',
  },
  production: {
    apiUrl: 'https://your-domain.com/api',
    telegramBotUrl: 'https://t.me/PremiumCarAlertBot',
  },
};

export default config[process.env.NODE_ENV || 'development'];
```

## 🧪 Testing

### 1. Unit Testing

```bash
# Install testing dependencies
npm install --save-dev jest @testing-library/react-native

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

### 2. E2E Testing

```bash
# Install Detox for E2E testing
npm install --save-dev detox

# Run E2E tests
npm run e2e:ios
npm run e2e:android
```

### 3. Testing Strategy

```typescript
// Test authentication flow
describe('Authentication', () => {
  it('should register new user', async () => {
    // Test registration form
    // Verify API calls
    // Check navigation
  });
  
  it('should login existing user', async () => {
    // Test login form
    // Verify token storage
    // Check app state
  });
});

// Test notification handling
describe('Notifications', () => {
  it('should handle car alert notification', async () => {
    // Simulate notification
    // Test deep linking
    // Verify screen navigation
  });
});
```

## 📊 Performance Optimization

### 1. Bundle Size Optimization

```typescript
// Use dynamic imports for large screens
const SubscriptionScreen = lazy(() => import('./screens/SubscriptionScreen'));

// Optimize images
import { Image } from 'expo-image';

// Use FlatList for large lists
import { FlatList } from 'react-native';
```

### 2. State Management

```typescript
// Optimize re-renders with Zustand
const useCarStore = create((set) => ({
  cars: [],
  filters: {},
  
  // Only update specific parts of state
  updateFilters: (newFilters) => set((state) => ({
    filters: { ...state.filters, ...newFilters }
  })),
}));
```

## 🚀 Deployment Checklist

- [ ] App configuration completed
- [ ] All screens implemented
- [ ] Authentication flow tested
- [ ] API integration working
- [ ] Push notifications configured
- [ ] Deep linking tested
- [ ] App icons and splash screen added
- [ ] Store listings prepared
- [ ] Privacy policy and terms added
- [ ] Beta testing completed
- [ ] Production builds created
- [ ] Store submissions approved

## 📱 Store Submission

### 1. App Store (iOS)

```bash
# Required assets:
- App icons (all sizes)
- Screenshots (all device sizes)
- App preview video
- Privacy policy URL
- Support URL
- App description
- Keywords
- Age rating

# Submission process:
1. Create App Store Connect record
2. Upload build via EAS Submit
3. Fill app information
4. Submit for review
5. Monitor review status
```

### 2. Google Play (Android)

```bash
# Required assets:
- App icons and feature graphic
- Screenshots (phone and tablet)
- App description
- Privacy policy URL
- Content rating
- Target audience

# Submission process:
1. Create Google Play Console record
2. Upload AAB via EAS Submit
3. Fill store listing
4. Set up release
5. Submit for review
```

---

## 🎉 Development Complete!

Your Premium Car Alert mobile app is now ready for deployment with:

✅ **Professional React Native architecture**  
✅ **Secure authentication system**  
✅ **Real-time push notifications**  
✅ **Telegram bot integration**  
✅ **Premium subscription management**  
✅ **AI damage detection interface**  
✅ **Production-ready build system**

**Next Steps**: Build, test, and submit to app stores!

---

*For technical support during development, refer to the Expo documentation or contact the development team.*