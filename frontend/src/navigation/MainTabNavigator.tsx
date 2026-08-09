import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Text } from "react-native";
import HomeScreen from "../screens/HomeScreen";
import SearchScreen from "../screens/SearchScreen";
import LibraryScreen from "../screens/LibraryScreen";
import InsightsScreen from "../screens/InsightsScreen";
import ProfileScreen from "../screens/ProfileScreen";
import { useTheme } from "../theme/ThemeContext";

export type MainTabParamList = {
  Home: undefined;
  Search: undefined;
  Library: undefined;
  Insights: undefined;
  Profile: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();

const tabIcon = (emoji: string) => ({ color }: { color: string }) => (
  <Text style={{ fontSize: 20, color }}>{emoji}</Text>
);

export default function MainTabNavigator() {
  const { theme, typography } = useTheme();

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: theme.background.primary,
          borderTopColor: theme.border.default,
          borderTopWidth: 1,
          height: 64,
        },
        tabBarActiveTintColor: theme.brand.primary,
        tabBarInactiveTintColor: theme.text.muted,
        tabBarLabelStyle: typography["nav-link"],
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{ tabBarIcon: tabIcon("🏠") }}
      />
      <Tab.Screen
        name="Search"
        component={SearchScreen}
        options={{ tabBarIcon: tabIcon("🔍") }}
      />
      <Tab.Screen
        name="Library"
        component={LibraryScreen}
        options={{ tabBarIcon: tabIcon("📖") }}
      />
      <Tab.Screen
        name="Insights"
        component={InsightsScreen}
        options={{ tabBarIcon: tabIcon("📊") }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ tabBarIcon: tabIcon("👤") }}
      />
    </Tab.Navigator>
  );
}