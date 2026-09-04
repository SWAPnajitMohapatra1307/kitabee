import React, { useEffect, useState } from "react";
import { View, ActivityIndicator } from "react-native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { useUserStore } from "../stores/userStore";
import { api, clearAuthToken } from "../services/api";
import AuthNavigator from "./AuthNavigator";
import MainTabNavigator from "./MainTabNavigator";
import OnboardingNavigator from "./OnboardingNavigator";

const Stack = createNativeStackNavigator();

export default function RootNavigator() {
  const isAuthenticated = useUserStore((s) => s.isAuthenticated);
  const user = useUserStore((s) => s.user);
  const hasHydrated = useUserStore((s) => s.hasHydrated);
  const setUser = useUserStore((s) => s.setUser);
  const logout = useUserStore((s) => s.logout);

  // true until persist rehydration + optional token verify finish
  const [isVerifying, setIsVerifying] = useState(true);

  useEffect(() => {
    if (!hasHydrated) return;

    let isMounted = true;

    const verifySession = async () => {
      // Not logged in → skip network, go straight to Auth
      if (!isAuthenticated) {
        if (isMounted) setIsVerifying(false);
        return;
      }

      try {
        const res = await api.get("/users/me");
        if (!isMounted) return;

        // Backend is source of truth for onboarding_completed
        const me = res.data?.user ?? res.data;
        setUser(me);
      } catch (error: any) {
        const status = error?.response?.status;

        if (status === 401) {
          console.log("[RootNavigator] 401 — clearing session");
          await clearAuthToken();
          if (isMounted) {
            // hard reset without depending on logout async timing
            useUserStore.setState({ user: null, isAuthenticated: false });
          }
        } else {
          // Network blip: keep persisted user, do NOT force onboarding
          console.log("[RootNavigator] verify failed (non-401), using cache", status);
        }
      } finally {
        if (isMounted) setIsVerifying(false);
      }
    };

    verifySession();

    return () => {
      isMounted = false;
    };
  }, [hasHydrated, isAuthenticated, setUser]);

  // ── Guards ──────────────────────────────────────────────

  // Still loading persisted state OR hitting /users/me
  if (!hasHydrated || isVerifying) {
    return (
      <View
        style={{
          flex: 1,
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#0B0B0E",
        }}
      >
        <ActivityIndicator size="large" color="#E2B13C" />
      </View>
    );
  }

  // Only show onboarding when we *know* it's incomplete.
  // If user is missing fields, prefer Main over trapping them in onboarding.
  const showOnboarding =
    isAuthenticated &&
    user != null &&
    user.onboarding_completed === false;

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