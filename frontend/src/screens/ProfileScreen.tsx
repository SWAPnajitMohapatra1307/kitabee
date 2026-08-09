import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { useTheme } from "../theme/ThemeContext";
import { authService } from '../services/auth';
import { Button } from '../components/Button';

export default function ProfileScreen() {
  const { theme, typography, spacing } = useTheme();
  return (
    <View style={[styles.container, { backgroundColor: theme.background.primary }]}>
      <Text style={[typography["display-lg"], { color: theme.text.primary }]}>
        👤 Profile
      </Text>
      <Button
        title="LOG OUT"
        variant="outline"
        onPress={authService.logout}
        style={{ marginTop: spacing.md, width: '80%' }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: "center", justifyContent: "center" },
});