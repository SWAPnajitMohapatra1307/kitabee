import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import ContentChoiceScreen from "../screens/onboarding/ContentChoiceScreen";
import GenreSelectionScreen from "../screens/onboarding/GenreSelectionScreen";
import RateInitialContentScreen from "../screens/onboarding/RateInitialContentScreen";

export type OnboardingStackParamList = {
  ContentChoice: undefined;
  GenreSelection: { contentType: "books" | "comics" | "both" };
  RateInitialContent: { contentType: "books" | "comics" | "both"; genres: string[] };
};

const Stack = createNativeStackNavigator<OnboardingStackParamList>();

export default function OnboardingNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false, animation: "slide_from_right" }}>
      <Stack.Screen name="ContentChoice" component={ContentChoiceScreen} />
      <Stack.Screen name="GenreSelection" component={GenreSelectionScreen} />
      <Stack.Screen name="RateInitialContent" component={RateInitialContentScreen} />
    </Stack.Navigator>
  );
}