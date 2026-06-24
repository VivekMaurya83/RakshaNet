import React from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';

export default function ScamAnalyzerScreen() {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      {/* Live Monitor */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Live VoIP Listener</Text>
        <Text style={styles.cardText}>
          Real-time speech transcript monitoring for potential digital arrest triggers over WebSockets.
        </Text>
        <View style={styles.statusBox}>
          <Text style={styles.transcriptText}>
            [Live Transcript] "This is Delhi Customs... illegal package..."
          </Text>
        </View>
        <View style={styles.alertCritical}>
          <Text style={styles.alertText}>⚠️ DIGITAL ARREST IMPERSONATION DETECTED</Text>
        </View>
      </View>

      {/* Audio Uploader */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Upload Audio File</Text>
        <Text style={styles.cardText}>
          Record calls and upload the file (MP3/M4A) to Firebase Storage for entity extraction.
        </Text>
        <TouchableOpacity style={styles.button}>
          <Text style={styles.buttonText}>Upload call_recording.mp3</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    gap: 20,
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
  statusBox: {
    backgroundColor: '#0f172a',
    borderRadius: 8,
    padding: 12,
    marginBottom: 15,
  },
  transcriptText: {
    color: '#dc2626',
    fontStyle: 'italic',
    fontSize: 13,
  },
  alertCritical: {
    backgroundColor: '#7f1d1d',
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
    marginBottom: 15,
  },
  alertText: {
    color: '#fecaca',
    fontWeight: 'bold',
    fontSize: 11,
  },
  button: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  buttonText: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
});
