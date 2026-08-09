import React from "react";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { NavigationContainer } from "@react-navigation/native";
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
        <NavigationContainer>
          <AppInner />
        </NavigationContainer>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}