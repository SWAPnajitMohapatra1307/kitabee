import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { useTheme } from "../../theme/ThemeContext";
import { OnboardingStackParamList } from "../../navigation/OnboardingNavigator";

type Nav = NativeStackNavigationProp<OnboardingStackParamList, "ContentChoice">;

const OPTIONS: {
  key: "books" | "comics" | "both";
  label: string;
  subtitle: string;
  icon: keyof typeof Ionicons.glyphMap;
}[] = [
  {
    key: "books",
    label: "Books",
    subtitle: "Fiction, non-fiction, classics and more",
    icon: "book-outline",
  },
  {
    key: "comics",
    label: "Comics",
    subtitle: "Graphic novels, manga, superhero runs",
    icon: "albums-outline",
  },
  {
    key: "both",
    label: "Both",
    subtitle: "Show me everything",
    icon: "library-outline",
  },
];

export default function ContentChoiceScreen() {
  const { theme, typography, spacing, rounded } = useTheme();
  const navigation = useNavigation<Nav>();
  const [selected, setSelected] = useState<"books" | "comics" | "both" | null>(null);

  const handleContinue = () => {
    if (!selected) return;
    navigation.navigate("GenreSelection", { contentType: selected });
  };

  return (
    <SafeAreaView style={[styles.root, { backgroundColor: theme.background.primary }]}>
      <View style={[styles.inner, { paddingHorizontal: spacing.sm }]}>
        {/* Header */}
        <View style={styles.headerBlock}>
          <Text style={[typography["display-lg"], { color: theme.brand.primary }]}>
            Kitabee
          </Text>
          <Text
            style={[
              typography["display-md"],
              { color: theme.text.primary, marginTop: spacing.xs },
            ]}
          >
            What do you love to read?
          </Text>
          <Text
            style={[
              typography["body-md"],
              { color: theme.text.secondary, marginTop: spacing.xxs },
            ]}
          >
            We'll personalise your feed based on this.
          </Text>
        </View>

        {/* Options */}
        <View style={[styles.optionsBlock, { gap: spacing.xxs }]}>
          {OPTIONS.map((opt) => {
            const active = selected === opt.key;
            return (
              <TouchableOpacity
                key={opt.key}
                onPress={() => setSelected(opt.key)}
                activeOpacity={0.75}
                style={[
                  styles.optionCard,
                  {
                    backgroundColor: active
                      ? theme.background.elevated
                      : theme.background.card,
                    borderRadius: rounded.lg,
                    borderWidth: 2,
                    borderColor: active
                      ? theme.brand.primary
                      : "transparent",
                    padding: spacing.sm,
                  },
                ]}
              >
                <View
                  style={[
                    styles.iconWrap,
                    {
                      backgroundColor: active
                        ? theme.brand.primary
                        : theme.background.elevated,
                      borderRadius: rounded.md,
                    },
                  ]}
                >
                  <Ionicons
                    name={opt.icon}
                    size={28}
                    color={active ? theme.brand.onPrimary : theme.text.secondary}
                  />
                </View>
                <View style={{ flex: 1, marginLeft: spacing.xs }}>
                  <Text
                    style={[typography["title-md"], { color: theme.text.primary }]}
                  >
                    {opt.label}
                  </Text>
                  <Text
                    style={[
                      typography["body-sm"],
                      { color: theme.text.secondary, marginTop: 2 },
                    ]}
                  >
                    {opt.subtitle}
                  </Text>
                </View>
                {active && (
                  <Ionicons
                    name="checkmark-circle"
                    size={22}
                    color={theme.brand.primary}
                  />
                )}
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Continue */}
        <TouchableOpacity
          onPress={handleContinue}
          disabled={!selected}
          activeOpacity={0.8}
          style={[
            styles.continueBtn,
            {
              backgroundColor: theme.brand.primary,
              borderRadius: rounded.none,
              opacity: selected ? 1 : 0.4,
            },
          ]}
        >
          <Text style={[typography["button"], { color: theme.brand.onPrimary }]}>
            Continue
          </Text>
        </TouchableOpacity>

        {/* Step indicator */}
        <View style={styles.stepRow}>
          <View style={[styles.stepDot, { backgroundColor: theme.brand.primary }]} />
          <View style={[styles.stepDot, { backgroundColor: theme.background.elevated }]} />
          <View style={[styles.stepDot, { backgroundColor: theme.background.elevated }]} />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  inner: { flex: 1, justifyContent: "center" },
  headerBlock: { marginBottom: 40 },
  optionsBlock: { marginBottom: 40 },
  optionCard: {
    flexDirection: "row",
    alignItems: "center",
  },
  iconWrap: {
    width: 52,
    height: 52,
    alignItems: "center",
    justifyContent: "center",
  },
  continueBtn: {
    height: 52,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 24,
  },
  stepRow: {
    flexDirection: "row",
    justifyContent: "center",
    gap: 8,
  },
  stepDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
});