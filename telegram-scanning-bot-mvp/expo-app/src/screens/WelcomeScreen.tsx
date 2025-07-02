import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  SafeAreaView,
  Dimensions,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

import { RootStackParamList } from '../../App';

type WelcomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Welcome'>;

const { width, height } = Dimensions.get('window');

export default function WelcomeScreen() {
  const navigation = useNavigation<WelcomeScreenNavigationProp>();

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={['#1a1a2e', '#16213e', '#0f3460']}
        style={styles.gradient}
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.logoContainer}>
            <Ionicons name="car-sport" size={60} color="#0066ff" />
            <Text style={styles.logoText}>Premium Car Alert</Text>
          </View>
          <Text style={styles.tagline}>
            AI-Powered Car Listing Alerts with Damage Detection
          </Text>
        </View>

        {/* Features */}
        <View style={styles.featuresContainer}>
          <View style={styles.feature}>
            <Ionicons name="notifications" size={32} color="#0066ff" />
            <Text style={styles.featureTitle}>Instant Alerts</Text>
            <Text style={styles.featureDescription}>
              Get notified immediately when cars matching your criteria are listed
            </Text>
          </View>

          <View style={styles.feature}>
            <Ionicons name="eye" size={32} color="#0066ff" />
            <Text style={styles.featureTitle}>AI Damage Detection</Text>
            <Text style={styles.featureDescription}>
              Advanced YOLOv8 AI analyzes car images for damage assessment
            </Text>
          </View>

          <View style={styles.feature}>
            <Ionicons name="filter" size={32} color="#0066ff" />
            <Text style={styles.featureTitle}>Smart Filtering</Text>
            <Text style={styles.featureDescription}>
              Set precise filters for make, model, price, year, and location
            </Text>
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionContainer}>
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => navigation.navigate('Register')}
          >
            <Text style={styles.primaryButtonText}>Get Started</Text>
            <Ionicons name="arrow-forward" size={20} color="#fff" />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => navigation.navigate('Login')}
          >
            <Text style={styles.secondaryButtonText}>Already have an account?</Text>
          </TouchableOpacity>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Connect with our Telegram bot for instant notifications
          </Text>
          <TouchableOpacity style={styles.telegramButton}>
            <Ionicons name="paper-plane" size={16} color="#0066ff" />
            <Text style={styles.telegramButtonText}>@PremiumCarAlertBot</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
    paddingHorizontal: 20,
  },
  header: {
    alignItems: 'center',
    marginTop: height * 0.08,
    marginBottom: height * 0.06,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 16,
  },
  logoText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 12,
    fontFamily: 'Inter-Bold',
  },
  tagline: {
    fontSize: 16,
    color: '#b0b0b0',
    textAlign: 'center',
    lineHeight: 24,
    fontFamily: 'Inter-Regular',
  },
  featuresContainer: {
    flex: 1,
    justifyContent: 'center',
    paddingVertical: 20,
  },
  feature: {
    alignItems: 'center',
    marginBottom: 40,
    paddingHorizontal: 20,
  },
  featureTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginTop: 12,
    marginBottom: 8,
    fontFamily: 'Inter-SemiBold',
  },
  featureDescription: {
    fontSize: 14,
    color: '#b0b0b0',
    textAlign: 'center',
    lineHeight: 20,
    fontFamily: 'Inter-Regular',
  },
  actionContainer: {
    marginBottom: 30,
  },
  primaryButton: {
    backgroundColor: '#0066ff',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    shadowColor: '#0066ff',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    marginRight: 8,
    fontFamily: 'Inter-SemiBold',
  },
  secondaryButton: {
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#333',
  },
  secondaryButtonText: {
    color: '#b0b0b0',
    fontSize: 16,
    fontFamily: 'Inter-Regular',
  },
  footer: {
    alignItems: 'center',
    paddingBottom: 20,
  },
  footerText: {
    fontSize: 12,
    color: '#888',
    marginBottom: 8,
    fontFamily: 'Inter-Regular',
  },
  telegramButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: 'rgba(0, 102, 255, 0.1)',
  },
  telegramButtonText: {
    color: '#0066ff',
    fontSize: 12,
    marginLeft: 4,
    fontFamily: 'Inter-Medium',
  },
});