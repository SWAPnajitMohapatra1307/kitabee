import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { authService } from '../services/auth';

export default function LoginScreen({ navigation }: any) {
  const { theme, typography, spacing } = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) return Alert.alert('Error', 'Fill all fields');
    setLoading(true);
    try {
      await authService.login({ email, password });
      // Navigation happens automatically via RootNavigator auth gate
    } catch (err: any) {
      Alert.alert('Login Failed', err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background.primary }]}>
      <View style={styles.content}>
        <Text style={[typography['display-lg'], { color: theme.text.primary, marginBottom: spacing.lg }]}>
          Welcome Back
        </Text>
        
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
          title="LOG IN" 
          onPress={handleLogin} 
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