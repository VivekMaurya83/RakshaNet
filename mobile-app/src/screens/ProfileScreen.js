import React from 'react';
import { StyleSheet, Text, View, ScrollView } from 'react-native';

export default function ProfileScreen() {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Officer Profile</Text>
        <Text style={styles.cardText}>
          Credentials associated with the public safety dashboard authority.
        </Text>
        <View style={styles.detailsBox}>
          <Text style={styles.detailText}>Name: Officer Ramesh Sharma</Text>
          <Text style={styles.detailText}>Agency: Delhi Special Cell</Text>
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
  detailsBox: {
    backgroundColor: '#0f172a',
    borderRadius: 8,
    padding: 15,
  },
  detailText: {
    color: '#94a3b8',
    fontSize: 13,
    marginBottom: 5,
  },
});
