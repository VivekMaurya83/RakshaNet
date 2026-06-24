import React from 'react';
import { StyleSheet, Text, View, ScrollView } from 'react-native';

export default function HomeScreen() {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Emergency Incident Feed</Text>
        <Text style={styles.cardText}>
          Real-time cybercrime incidents and visual alert signals active across Delhi NCR region.
        </Text>
        <View style={styles.alertCount}>
          <Text style={styles.alertCountText}>12 Active Threat Alerts</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
  },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: '#334155',
  },
  cardTitle: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  cardText: {
    color: '#94a3b8',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 15,
  },
  alertCount: {
    backgroundColor: '#7f1d1d',
    padding: 10,
    borderRadius: 6,
    alignItems: 'center',
  },
  alertCountText: {
    color: '#fecaca',
    fontWeight: 'bold',
    fontSize: 13,
  },
});
