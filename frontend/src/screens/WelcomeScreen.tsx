import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { useTheme } from "../theme/ThemeContext";

export default function WelcomeScreen() {
  const { theme, typography } = useTheme();
  return (
    <View style={[styles.container, { backgroundColor: theme.background.primary }]}>
      <Text style={[typography["display-lg"], { color: theme.text.primary }]}>
        🐝 Welcome
      </Text>
      <Text style={[typography["body-md"], { color: theme.text.secondary, marginTop: 8 }]}>
        Kitabee
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: "center", justifyContent: "center" },
});