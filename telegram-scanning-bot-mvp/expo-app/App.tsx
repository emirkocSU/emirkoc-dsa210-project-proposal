import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { QueryClient, QueryClientProvider } from 'react-query';
import * as SplashScreen from 'expo-splash-screen';
import * as Font from 'expo-font';
import * as Notifications from 'expo-notifications';

// Screens
import WelcomeScreen from './src/screens/WelcomeScreen';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import MainTabNavigator from './src/navigation/MainTabNavigator';
import CarDetailsScreen from './src/screens/CarDetailsScreen';
import FilterScreen from './src/screens/FilterScreen';
import SubscriptionScreen from './src/screens/SubscriptionScreen';
import ProfileScreen from './src/screens/ProfileScreen';

// Store
import { useAuthStore } from './src/store/authStore';

// Utils
import { setupNotifications } from './src/utils/notifications';
import { linkingConfig } from './src/utils/linking';

// Types
export type RootStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  Main: undefined;
  CarDetails: { carId: string };
  Filter: undefined;
  Subscription: undefined;
  Profile: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();
const queryClient = new QueryClient();

// Configure notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// Prevent splash screen from auto-hiding
SplashScreen.preventAutoHideAsync();

export default function App() {
  const { isAuthenticated, isLoading, initializeAuth } = useAuthStore();
  const [appIsReady, setAppIsReady] = React.useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Load fonts
        await Font.loadAsync({
          'Inter-Regular': require('./assets/fonts/Inter-Regular.ttf'),
          'Inter-Medium': require('./assets/fonts/Inter-Medium.ttf'),
          'Inter-SemiBold': require('./assets/fonts/Inter-SemiBold.ttf'),
          'Inter-Bold': require('./assets/fonts/Inter-Bold.ttf'),
        });

        // Setup notifications
        await setupNotifications();

        // Initialize authentication
        await initializeAuth();

      } catch (e) {
        console.warn('Error during app initialization:', e);
      } finally {
        setAppIsReady(true);
      }
    }

    prepare();
  }, [initializeAuth]);

  const onLayoutRootView = React.useCallback(async () => {
    if (appIsReady) {
      await SplashScreen.hideAsync();
    }
  }, [appIsReady]);

  if (!appIsReady || isLoading) {
    return null;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <NavigationContainer linking={linkingConfig} onReady={onLayoutRootView}>
        <Stack.Navigator
          screenOptions={{
            headerShown: false,
            gestureEnabled: true,
            cardStyleInterpolator: ({ current, layouts }) => {
              return {
                cardStyle: {
                  transform: [
                    {
                      translateX: current.progress.interpolate({
                        inputRange: [0, 1],
                        outputRange: [layouts.screen.width, 0],
                      }),
                    },
                  ],
                },
              };
            },
          }}
        >
          {!isAuthenticated ? (
            // Authentication flow
            <>
              <Stack.Screen name="Welcome" component={WelcomeScreen} />
              <Stack.Screen name="Login" component={LoginScreen} />
              <Stack.Screen name="Register" component={RegisterScreen} />
            </>
          ) : (
            // Main app flow
            <>
              <Stack.Screen name="Main" component={MainTabNavigator} />
              <Stack.Screen 
                name="CarDetails" 
                component={CarDetailsScreen}
                options={{
                  headerShown: true,
                  title: 'Car Details',
                  headerStyle: {
                    backgroundColor: '#1a1a2e',
                  },
                  headerTintColor: '#fff',
                }}
              />
              <Stack.Screen 
                name="Filter" 
                component={FilterScreen}
                options={{
                  headerShown: true,
                  title: 'Search Filters',
                  headerStyle: {
                    backgroundColor: '#1a1a2e',
                  },
                  headerTintColor: '#fff',
                }}
              />
              <Stack.Screen 
                name="Subscription" 
                component={SubscriptionScreen}
                options={{
                  headerShown: true,
                  title: 'Premium Subscription',
                  headerStyle: {
                    backgroundColor: '#1a1a2e',
                  },
                  headerTintColor: '#fff',
                }}
              />
              <Stack.Screen 
                name="Profile" 
                component={ProfileScreen}
                options={{
                  headerShown: true,
                  title: 'Profile',
                  headerStyle: {
                    backgroundColor: '#1a1a2e',
                  },
                  headerTintColor: '#fff',
                }}
              />
            </>
          )}
        </Stack.Navigator>
        <StatusBar style="light" backgroundColor="#1a1a2e" />
      </NavigationContainer>
    </QueryClientProvider>
  );
}