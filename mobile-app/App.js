import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, SafeAreaView } from 'react-native';
import { StatusBar } from 'expo-status-bar';

// Import newly created screens
import HomeScreen from './src/screens/HomeScreen';
import ScamAnalyzerScreen from './src/screens/ScamAnalyzerScreen';
import CurrencyScannerScreen from './src/screens/CurrencyScannerScreen';
import DeepfakeAnalyzerScreen from './src/screens/DeepfakeAnalyzerScreen';
import ReportFraudScreen from './src/screens/ReportFraudScreen';
import ProfileScreen from './src/screens/ProfileScreen';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('Home');

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>RakshaNet</Text>
        <Text style={styles.headerSubtitle}>Public Safety Shield</Text>
      </View>

      {/* Screen Render Container */}
      <View style={styles.screenBody}>
        {currentScreen === 'Home' && <HomeScreen />}
        {currentScreen === 'Analyzer' && <ScamAnalyzerScreen />}
        {currentScreen === 'Scanner' && <CurrencyScannerScreen />}
        {currentScreen === 'Deepfake' && <DeepfakeAnalyzerScreen />}
        {currentScreen === 'Report' && <ReportFraudScreen />}
        {currentScreen === 'Profile' && <ProfileScreen />}
      </View>

      {/* Navigation Footer */}
      <View style={styles.footer}>
        {[
          { key: 'Home', label: 'Home' },
          { key: 'Analyzer', label: 'Analyzer' },
          { key: 'Scanner', label: 'Scanner' },
          { key: 'Deepfake', label: 'Deepfake' },
          { key: 'Report', label: 'Report' },
          { key: 'Profile', label: 'Profile' }
        ].map(screen => (
          <TouchableOpacity
            key={screen.key}
            onPress={() => setCurrentScreen(screen.key)}
            style={[
              styles.navButton,
              currentScreen === screen.key && styles.navButtonActive
            ]}
          >
            <Text
              style={[
                styles.navButtonText,
                currentScreen === screen.key && styles.navButtonTextActive
              ]}
            >
              {screen.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  header: {
    height: 70,
    backgroundColor: '#1e293b',
    justifyContent: 'center',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  headerTitle: {
    color: '#3b82f6',
    fontSize: 20,
    fontWeight: 'bold',
    letterSpacing: 1.5,
  },
  headerSubtitle: {
    color: '#94a3b8',
    fontSize: 11,
    textTransform: 'uppercase',
  },
  screenBody: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  footer: {
    height: 60,
    backgroundColor: '#1e293b',
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  navButton: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  navButtonActive: {
    backgroundColor: '#0f172a',
  },
  navButtonText: {
    color: '#64748b',
    fontSize: 10,
    fontWeight: '600',
  },
  navButtonTextActive: {
    color: '#3b82f6',
  },
});
