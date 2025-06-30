/**
 * Professional URL Scanner - Main App Component
 * Integrates with Telegram bot for seamless security scanning experience
 */

import React, { useEffect, useState, useCallback } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import * as Linking from 'expo-linking';
import * as SplashScreen from 'expo-splash-screen';
import { Ionicons } from '@expo/vector-icons';
import { Alert, Platform } from 'react-native';

// Screens
import LoginScreen from './screens/LoginScreen';
import RegisterScreen from './screens/RegisterScreen';
import HomeScreen from './screens/HomeScreen';
import LinkingScreen from './screens/LinkingScreen';
import ScanHistoryScreen from './screens/ScanHistoryScreen';
import SettingsScreen from './screens/SettingsScreen';

// Services and Utils
import { AuthProvider, useAuth } from './services/authService';
import { LinkingProvider } from './services/linkingService';
import { theme } from './theme/theme';

// Keep splash screen visible while we fetch resources
SplashScreen.preventAutoHideAsync();

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Tab Navigator for authenticated users
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'History') {
            iconName = focused ? 'list' : 'list-outline';
          } else if (route.name === 'Linking') {
            iconName = focused ? 'link' : 'link-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.onSurfaceVariant,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.outline,
          paddingBottom: Platform.OS === 'ios' ? 20 : 5,
          height: Platform.OS === 'ios' ? 85 : 60,
        },
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: theme.colors.onPrimary,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          title: 'Scanner',
          headerTitle: '🛡️ Professional Scanner',
        }}
      />
      <Tab.Screen 
        name="History" 
        component={ScanHistoryScreen}
        options={{
          title: 'History',
          headerTitle: '📊 Scan History',
        }}
      />
      <Tab.Screen 
        name="Linking" 
        component={LinkingScreen}
        options={{
          title: 'Telegram',
          headerTitle: '🔗 Telegram Link',
        }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{
          title: 'Settings',
          headerTitle: '⚙️ Settings',
        }}
      />
    </Tab.Navigator>
  );
}

// Auth Stack for non-authenticated users
function AuthStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: theme.colors.onPrimary,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="Login" 
        component={LoginScreen}
        options={{
          title: '🛡️ Professional Scanner',
          headerBackVisible: false,
        }}
      />
      <Stack.Screen 
        name="Register" 
        component={RegisterScreen}
        options={{
          title: 'Create Account',
        }}
      />
    </Stack.Navigator>
  );
}

// Main App Navigation
function AppNavigator() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    // Keep splash screen visible while loading
    return null;
  }

  return (
    <NavigationContainer
      linking={{
        prefixes: ['scanapp://', 'https://professionalscan.app'],
        config: {
          screens: {
            MainTabs: {
              screens: {
                Home: 'home',
                History: 'history',
                Linking: 'linking',
                Settings: 'settings',
              },
            },
            Auth: {
              screens: {
                Login: 'login',
                Register: 'register',
              },
            },
          },
        },
      }}
      onReady={() => {
        // Hide splash screen when navigation is ready
        SplashScreen.hideAsync();
      }}
    >
      {user ? <MainTabs /> : <AuthStack />}
    </NavigationContainer>
  );
}

// Deep Link Handler Component
function DeepLinkHandler() {
  const { user } = useAuth();

  useEffect(() => {
    // Handle deep links when app is already running
    const subscription = Linking.addEventListener('url', handleDeepLink);

    // Handle deep link when app is opened from closed state
    Linking.getInitialURL().then((url) => {
      if (url) {
        handleDeepLink({ url });
      }
    });

    return () => subscription?.remove();
  }, [user]);

  const handleDeepLink = useCallback(({ url }) => {
    console.log('Deep link received:', url);

    if (!url) return;

    try {
      const { hostname, pathname, queryParams } = Linking.parse(url);
      
      // Handle different deep link scenarios
      if (hostname === 'auth' || pathname === '/auth') {
        // Handle authentication deep links from Telegram bot
        const token = queryParams?.token;
        if (token && user) {
          // Process authentication token
          console.log('Auth token received:', token);
          // This would trigger the linking process
        }
      } else if (hostname === 'results' || pathname?.startsWith('/results')) {
        // Handle scan results deep links
        const scanId = queryParams?.id || pathname?.split('/').pop();
        if (scanId) {
          console.log('Scan result deep link:', scanId);
          // Navigate to specific scan result
        }
      }
    } catch (error) {
      console.error('Error parsing deep link:', error);
      Alert.alert(
        'Link Error',
        'Unable to process the link. Please try again.',
        [{ text: 'OK' }]
      );
    }
  }, [user]);

  return null;
}

// Main App Component
export default function App() {
  const [appIsReady, setAppIsReady] = useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Pre-load fonts, make any API calls you need to do here
        // For now, we'll just simulate loading time
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (e) {
        console.warn('Error during app preparation:', e);
      } finally {
        // Tell the application to render
        setAppIsReady(true);
      }
    }

    prepare();
  }, []);

  if (!appIsReady) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <AuthProvider>
          <LinkingProvider>
            <DeepLinkHandler />
            <AppNavigator />
            <StatusBar style="light" backgroundColor={theme.colors.primary} />
          </LinkingProvider>
        </AuthProvider>
      </PaperProvider>
    </SafeAreaProvider>
  );
}

// App Configuration
const linking = {
  prefixes: ['scanapp://', 'https://professionalscan.app'],
  config: {
    screens: {
      Home: 'home',
      History: 'history',
      Linking: 'linking',
      Settings: 'settings',
      Login: 'login',
      Register: 'register',
    },
  },
};

// Export app info for debugging
export const appInfo = {
  name: 'Professional Scanner',
  version: '1.0.0',
  buildNumber: '1',
  scheme: 'scanapp',
  description: 'Professional URL Scanner with Telegram Integration',
};