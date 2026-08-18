import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { useUserStore } from "../stores/userStore";
import AuthNavigator from "./AuthNavigator";
import MainTabNavigator from "./MainTabNavigator";
import OnboardingNavigator from "./OnboardingNavigator";

const Stack = createNativeStackNavigator();

export default function RootNavigator() {
  const isAuthenticated = useUserStore((s) => s.isAuthenticated);
  const user = useUserStore((s) => s.user);

  const showOnboarding = isAuthenticated && user && !user.onboarding_completed;

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!isAuthenticated ? (
        <Stack.Screen name="Auth" component={AuthNavigator} />
      ) : showOnboarding ? (
        <Stack.Screen name="Onboarding" component={OnboardingNavigator} />
      ) : (
        <Stack.Screen name="Main" component={MainTabNavigator} />
      )}
    </Stack.Navigator>
  );
}