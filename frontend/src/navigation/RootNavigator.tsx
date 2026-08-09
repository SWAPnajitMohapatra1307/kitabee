import React from "react";
import { NavigationContainer, DefaultTheme, DarkTheme } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import AuthNavigator from "./AuthNavigator";
import MainTabNavigator from "./MainTabNavigator";
import { useTheme } from "../theme/ThemeContext";

export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function RootNavigator() {
  const { activeMode, theme } = useTheme();

  const navTheme =
    activeMode === "dark"
      ? {
          ...DarkTheme,
          colors: {
            ...DarkTheme.colors,
            background: theme.background.primary,
            card: theme.background.primary,
            text: theme.text.primary,
            border: theme.border.default,
            primary: theme.brand.primary,
          },
        }
      : {
          ...DefaultTheme,
          colors: {
            ...DefaultTheme.colors,
            background: theme.background.primary,
            card: theme.background.primary,
            text: theme.text.primary,
            border: theme.border.default,
            primary: theme.brand.primary,
          },
        };

  return (
    <NavigationContainer theme={navTheme}>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Auth" component={AuthNavigator} />
        <Stack.Screen name="Main" component={MainTabNavigator} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}