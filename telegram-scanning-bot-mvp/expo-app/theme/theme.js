/**
 * Professional Material Design Theme
 * Modern color palette and typography for the scanning app
 */

import { MD3LightTheme, MD3DarkTheme } from 'react-native-paper';

// Custom color palette
const colors = {
  // Primary brand colors
  primary: '#4f46e5',        // Indigo 600
  primaryVariant: '#3730a3', // Indigo 700
  onPrimary: '#ffffff',
  primaryContainer: '#e0e7ff', // Indigo 100
  onPrimaryContainer: '#1e1b4b', // Indigo 900

  // Secondary colors
  secondary: '#06b6d4',      // Cyan 500
  secondaryVariant: '#0891b2', // Cyan 600
  onSecondary: '#ffffff',
  secondaryContainer: '#cffafe', // Cyan 50
  onSecondaryContainer: '#164e63', // Cyan 800

  // Background colors
  background: '#f8fafc',     // Slate 50
  onBackground: '#0f172a',   // Slate 900
  surface: '#ffffff',
  onSurface: '#1e293b',      // Slate 800
  surfaceVariant: '#f1f5f9', // Slate 100
  onSurfaceVariant: '#64748b', // Slate 500

  // Status colors
  success: '#10b981',        // Emerald 500
  onSuccess: '#ffffff',
  successContainer: '#d1fae5', // Emerald 100
  onSuccessContainer: '#065f46', // Emerald 800

  warning: '#f59e0b',        // Amber 500
  onWarning: '#ffffff',
  warningContainer: '#fef3c7', // Amber 100
  onWarningContainer: '#92400e', // Amber 700

  error: '#ef4444',          // Red 500
  onError: '#ffffff',
  errorContainer: '#fee2e2', // Red 100
  onErrorContainer: '#991b1b', // Red 800

  // Neutral colors
  outline: '#d1d5db',        // Gray 300
  outlineVariant: '#e5e7eb', // Gray 200
  shadow: '#000000',
  scrim: '#000000',
  inverseSurface: '#1e293b', // Slate 800
  inverseOnSurface: '#f1f5f9', // Slate 100
  inversePrimary: '#a5b4fc', // Indigo 300

  // Telegram brand colors
  telegram: '#0088cc',
  telegramDark: '#006699',

  // Security status colors
  safe: '#10b981',           // Emerald 500
  lowRisk: '#f59e0b',        // Amber 500
  mediumRisk: '#f97316',     // Orange 500
  highRisk: '#ef4444',       // Red 500
  critical: '#dc2626',       // Red 600
};

// Typography scale
const fonts = {
  displayLarge: {
    fontFamily: 'System',
    fontSize: 57,
    fontWeight: '400',
    lineHeight: 64,
    letterSpacing: -0.25,
  },
  displayMedium: {
    fontFamily: 'System',
    fontSize: 45,
    fontWeight: '400',
    lineHeight: 52,
    letterSpacing: 0,
  },
  displaySmall: {
    fontFamily: 'System',
    fontSize: 36,
    fontWeight: '400',
    lineHeight: 44,
    letterSpacing: 0,
  },
  headlineLarge: {
    fontFamily: 'System',
    fontSize: 32,
    fontWeight: '600',
    lineHeight: 40,
    letterSpacing: 0,
  },
  headlineMedium: {
    fontFamily: 'System',
    fontSize: 28,
    fontWeight: '600',
    lineHeight: 36,
    letterSpacing: 0,
  },
  headlineSmall: {
    fontFamily: 'System',
    fontSize: 24,
    fontWeight: '600',
    lineHeight: 32,
    letterSpacing: 0,
  },
  titleLarge: {
    fontFamily: 'System',
    fontSize: 22,
    fontWeight: '600',
    lineHeight: 28,
    letterSpacing: 0,
  },
  titleMedium: {
    fontFamily: 'System',
    fontSize: 16,
    fontWeight: '500',
    lineHeight: 24,
    letterSpacing: 0.15,
  },
  titleSmall: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '500',
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  bodyLarge: {
    fontFamily: 'System',
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 24,
    letterSpacing: 0.5,
  },
  bodyMedium: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 20,
    letterSpacing: 0.25,
  },
  bodySmall: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '400',
    lineHeight: 16,
    letterSpacing: 0.4,
  },
  labelLarge: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '500',
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  labelMedium: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    lineHeight: 16,
    letterSpacing: 0.5,
  },
  labelSmall: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    lineHeight: 16,
    letterSpacing: 0.5,
  },
};

// Light theme
export const lightTheme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    ...colors,
  },
  fonts: {
    ...MD3LightTheme.fonts,
    ...fonts,
  },
};

// Dark theme
export const darkTheme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: '#a5b4fc',        // Indigo 300
    primaryVariant: '#818cf8', // Indigo 400
    onPrimary: '#1e1b4b',      // Indigo 900
    primaryContainer: '#3730a3', // Indigo 700
    onPrimaryContainer: '#e0e7ff', // Indigo 100

    secondary: '#22d3ee',      // Cyan 400
    secondaryVariant: '#06b6d4', // Cyan 500
    onSecondary: '#164e63',    // Cyan 800
    secondaryContainer: '#0891b2', // Cyan 600
    onSecondaryContainer: '#cffafe', // Cyan 50

    background: '#0f172a',     // Slate 900
    onBackground: '#f1f5f9',   // Slate 100
    surface: '#1e293b',        // Slate 800
    onSurface: '#e2e8f0',      // Slate 200
    surfaceVariant: '#334155', // Slate 700
    onSurfaceVariant: '#94a3b8', // Slate 400

    outline: '#475569',        // Slate 600
    outlineVariant: '#334155', // Slate 700
    inverseSurface: '#f1f5f9', // Slate 100
    inverseOnSurface: '#1e293b', // Slate 800
    inversePrimary: '#4f46e5', // Indigo 600

    // Keep status colors consistent
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    telegram: '#0088cc',
    safe: '#10b981',
    lowRisk: '#f59e0b',
    mediumRisk: '#f97316',
    highRisk: '#ef4444',
    critical: '#dc2626',
  },
  fonts: {
    ...MD3DarkTheme.fonts,
    ...fonts,
  },
};

// Default theme (light)
export const theme = lightTheme;

// Theme utilities
export const themeUtils = {
  // Get risk color based on damage score
  getRiskColor: (damageScore) => {
    if (damageScore === 0) return colors.safe;
    if (damageScore <= 20) return colors.lowRisk;
    if (damageScore <= 50) return colors.mediumRisk;
    if (damageScore <= 80) return colors.highRisk;
    return colors.critical;
  },

  // Get risk text based on damage score
  getRiskText: (damageScore) => {
    if (damageScore === 0) return 'Safe';
    if (damageScore <= 20) return 'Low Risk';
    if (damageScore <= 50) return 'Medium Risk';
    if (damageScore <= 80) return 'High Risk';
    return 'Critical';
  },

  // Get risk icon based on damage score
  getRiskIcon: (damageScore) => {
    if (damageScore === 0) return '✅';
    if (damageScore <= 20) return '⚠️';
    if (damageScore <= 50) return '🟡';
    if (damageScore <= 80) return '🔴';
    return '💀';
  },

  // Get status color
  getStatusColor: (status) => {
    const statusColors = {
      success: colors.success,
      warning: colors.warning,
      error: colors.error,
      info: colors.primary,
      pending: colors.warning,
      completed: colors.success,
      failed: colors.error,
      cancelled: colors.outline,
    };
    return statusColors[status] || colors.outline;
  },

  // Common spacing values
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },

  // Common border radius values
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    full: 9999,
  },

  // Common shadow styles
  shadows: {
    sm: {
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.05,
      shadowRadius: 2,
      elevation: 1,
    },
    md: {
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 3,
    },
    lg: {
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 5,
    },
  },
};

// Export individual components for convenience
export { colors, fonts };