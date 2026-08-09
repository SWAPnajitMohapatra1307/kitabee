import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle } from 'react-native';
import { useTheme } from '../theme/ThemeContext';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'outline' | 'ghost';
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
}

export const Button = ({ title, onPress, variant = 'primary', loading, disabled, style }: ButtonProps) => {
  const { theme, typography, spacing, rounded, activeMode } = useTheme();

  const getStyles = () => {
    const base = {
      paddingVertical: spacing.xs,
      paddingHorizontal: spacing.md,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: rounded.none,
      minHeight: 48,
    };

    if (variant === 'primary') return {
      ...base,
      backgroundColor: theme.brand.primary,
    };
    if (variant === 'outline') return {
      ...base,
      backgroundColor: 'transparent',
      borderWidth: 1,
      borderColor: theme.border.default,
    };
    return base; // ghost
  };

  const getTextColor = () => {
    if (variant === 'primary') return '#000000'; // Amber always needs dark text
    return theme.text.primary;
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      style={[getStyles() as ViewStyle, style, (disabled || loading) && { opacity: 0.6 }]}
      activeOpacity={0.8}
    >
      {loading ? (
        <ActivityIndicator color={getTextColor()} />
      ) : (
        <Text style={[
          typography['button'],
          { color: getTextColor() }
        ]}>
          {title}
        </Text>
      )}
    </TouchableOpacity>
  );
};