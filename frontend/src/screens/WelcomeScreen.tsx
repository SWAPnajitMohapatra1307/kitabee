import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { Button } from '../components/Button';

export default function WelcomeScreen({ navigation }: any) {
  const { theme, typography, spacing } = useTheme();

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background.primary }]}>
      <View style={styles.content}>
        <View style={styles.hero}>
          <Text style={[typography['display-mega'], { color: theme.brand.primary }]}>
            KITABEE
          </Text>
          <Text style={[typography['title-sm'], { color: theme.text.secondary, marginTop: spacing.xxs }]}>
            Discover your next obsession.
          </Text>
        </View>

        <View style={styles.actions}>
          <Button 
            title="SIGN UP FREE" 
            onPress={() => navigation.navigate('Register')} 
            style={{ marginBottom: spacing.xs }}
          />
          <Button 
            title="LOG IN" 
            variant="outline" 
            onPress={() => navigation.navigate('Login')} 
          />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { flex: 1, padding: 24, justifyContent: 'space-between' },
  hero: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  actions: { width: '100%', paddingBottom: 20 },
});