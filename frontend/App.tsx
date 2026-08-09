import React from "react";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { ThemeProvider, useTheme } from "./src/theme/ThemeContext";
import RootNavigator from "./src/navigation/RootNavigator";

function AppInner() {
  const { activeMode } = useTheme();
  return (
    <>
      <StatusBar style={activeMode === "dark" ? "light" : "dark"} />
      <RootNavigator />
    </>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <AppInner />
      </ThemeProvider>
    </SafeAreaProvider>
  );
}