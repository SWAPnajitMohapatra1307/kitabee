import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { authService } from '../services/auth';

export default function RegisterScreen({ navigation }: any) {
  const { theme, typography, spacing } = useTheme();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!fullName || !email || !password) return Alert.alert('Error', 'Fill all fields');
    if (password.length < 8) return Alert.alert('Error', 'Password must be at least 8 characters');
    setLoading(true);
    try {
      await authService.register({name: fullName, email, password });
      // Navigation happens automatically via RootNavigator auth gate
    } catch (err: any) {
      Alert.alert('Registration Failed', err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background.primary }]}>
      <View style={styles.content}>
        <Text style={[typography['display-lg'], { color: theme.text.primary, marginBottom: spacing.lg }]}>
          Create Account
        </Text>

        <Input
          label="FULL NAME"
          value={fullName}
          onChangeText={setFullName}
          autoCapitalize="words"
        />
        <Input
          label="EMAIL"
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
        />
        <Input
          label="PASSWORD"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        <Button
          title="CREATE ACCOUNT"
          onPress={handleRegister}
          loading={loading}
          style={{ marginTop: spacing.md }}
        />

        <Button
          title="BACK"
          variant="ghost"
          onPress={() => navigation.goBack()}
          style={{ marginTop: spacing.xs }}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 24, justifyContent: 'center', flex: 1 },
});