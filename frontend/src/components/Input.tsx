import React from 'react';
import { View, TextInput, Text, StyleSheet, TextInputProps } from 'react-native';
import { useTheme } from '../theme/ThemeContext';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
}

export const Input = ({ label, error, ...props }: InputProps) => {
  const { theme, typography, spacing, rounded } = useTheme();

  return (
    <View style={{ marginBottom: spacing.sm, width: '100%' }}>
      {label && (
        <Text style={[typography['caption-uppercase'], { color: theme.text.secondary, marginBottom: 4 }]}>
          {label}
        </Text>
      )}
      <TextInput
        style={[
          typography['body-md'],
          {
            backgroundColor: theme.background.elevated,
            color: theme.text.primary,
            padding: spacing.xs,
            borderRadius: rounded.none,
            borderWidth: 1,
            borderColor: error ? '#FF4444' : theme.border.default,
          }
        ]}
        placeholderTextColor={theme.text.muted}
        {...props}
      />
      {error && (
        <Text style={[typography.caption, { color: '#FF4444', marginTop: 4 }]}>
          {error}
        </Text>
      )}
    </View>
  );
};