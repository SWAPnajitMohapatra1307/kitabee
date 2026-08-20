import React from "react";
import { View, Text } from "react-native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";
import HomeStackNavigator from "./HomeStackNavigator";
import SearchScreen from "../screens/SearchScreen";
import LibraryScreen from "../screens/LibraryScreen";
import InsightsScreen from "../screens/InsightsScreen";
import ProfileStackNavigator from "./ProfileStackNavigator";
import { useTheme } from "../theme/ThemeContext";

export type MainTabParamList = {
  Home: undefined;
  Search: undefined;
  Library: undefined;
  Insights: undefined;
  Profile: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();

interface TabIconProps {
  name: keyof typeof Ionicons.glyphMap;
  color: string;
  focused: boolean;
}

function TabIcon({ name, color, focused }: TabIconProps) {
  const { theme } = useTheme();
  return (
    <View style={{ alignItems: "center", justifyContent: "center", width: 48 }}>
      <View
        style={{
          height: 2,
          width: 24,
          backgroundColor: focused ? theme.brand.primary : "transparent",
          marginBottom: 6,
        }}
      />
      <Ionicons name={name} size={22} color={color} />
    </View>
  );
}

interface TabLabelProps {
  label: string;
  color: string;
  focused: boolean;
}

function TabLabel({ label, color, focused }: TabLabelProps) {
  const { typography } = useTheme();
  return (
    <Text
      style={[
        typography["nav-link"],
        {
          color,
          fontSize: 10,
          marginTop: 2,
          fontWeight: focused ? "700" : "600",
        },
      ]}
    >
      {label}
    </Text>
  );
}

export default function MainTabNavigator() {
  const { theme } = useTheme();

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: theme.background.primary,
          borderTopColor: theme.border.default,
          borderTopWidth: 1,
          height: 68,
          paddingTop: 4,
          paddingBottom: 8,
        },
        tabBarActiveTintColor: theme.brand.primary,
        tabBarInactiveTintColor: theme.text.muted,
        tabBarShowLabel: true,
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeStackNavigator}
        options={{
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? "home" : "home-outline"} color={color} focused={focused} />
          ),
          tabBarLabel: ({ color, focused }) => (
            <TabLabel label="HOME" color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Search"
        component={SearchScreen}
        options={{
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? "search" : "search-outline"} color={color} focused={focused} />
          ),
          tabBarLabel: ({ color, focused }) => (
            <TabLabel label="SEARCH" color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Library"
        component={LibraryScreen}
        options={{
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? "library" : "library-outline"} color={color} focused={focused} />
          ),
          tabBarLabel: ({ color, focused }) => (
            <TabLabel label="LIBRARY" color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Insights"
        component={InsightsScreen}
        options={{
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? "stats-chart" : "stats-chart-outline"} color={color} focused={focused} />
          ),
          tabBarLabel: ({ color, focused }) => (
           <TabLabel label="INSIGHTS" color={color} focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileStackNavigator}
        options={{
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? "person" : "person-outline"} color={color} focused={focused} />
          ),
          tabBarLabel: ({ color, focused }) => (
            <TabLabel label="PROFILE" color={color} focused={focused} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}