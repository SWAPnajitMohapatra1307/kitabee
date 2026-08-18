import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  SafeAreaView,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useNavigation, useRoute, RouteProp } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useTheme } from "../../theme/ThemeContext";
import { api } from "../../services/api";
import { OnboardingStackParamList } from "../../navigation/OnboardingNavigator";

type Nav = NativeStackNavigationProp<OnboardingStackParamList, "GenreSelection">;
type Route = RouteProp<OnboardingStackParamList, "GenreSelection">;

const BOOK_GENRES = [
  "Fantasy", "Science Fiction", "Mystery", "Thriller", "Romance",
  "Historical Fiction", "Literary Fiction", "Horror", "Biography",
  "Self-Help", "Philosophy", "Psychology", "Science", "History",
  "Business", "Travel", "Poetry", "Classics", "Young Adult", "Children",
];

const COMIC_GENRES = [
  "Superhero", "Manga", "Graphic Novel", "Action", "Adventure",
  "Horror", "Sci-Fi", "Fantasy", "Slice of Life", "Comedy",
  "Crime", "War", "Western", "Romance", "Biography",
];

const BOTH_GENRES = [...new Set([...BOOK_GENRES, ...COMIC_GENRES])];

export default function GenreSelectionScreen() {
  const { theme, typography, spacing, rounded } = useTheme();
  const navigation = useNavigation<Nav>();
  const route = useRoute<Route>();
  const { contentType } = route.params;

  const genres =
    contentType === "books"
      ? BOOK_GENRES
      : contentType === "comics"
      ? COMIC_GENRES
      : BOTH_GENRES;

  const [selected, setSelected] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);

  const toggle = (genre: string) => {
    setSelected((prev) =>
      prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre]
    );
  };

  const handleContinue = async () => {
    if (selected.length < 3) {
      Alert.alert("Pick at least 3 genres", "This helps us find books you'll love.");
      return;
    }
    setSaving(true);
    try {
      await api.put("/users/me/preferences", {
        favorite_genres: selected,
      });
      navigation.navigate("RateInitialContent", {
        contentType,
        genres: selected,
      });
    } catch (err: any) {
      Alert.alert("Error", "Failed to save preferences. Try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <SafeAreaView style={[styles.root, { backgroundColor: theme.background.primary }]}>
      {/* Header */}
      <View style={[styles.header, { paddingHorizontal: spacing.sm }]}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={{ padding: 4, marginBottom: spacing.xxs }}
        >
          <Text style={[typography["body-md"], { color: theme.brand.primary }]}>
            ← Back
          </Text>
        </TouchableOpacity>
        <Text style={[typography["display-md"], { color: theme.text.primary }]}>
          Pick your genres
        </Text>
        <Text
          style={[
            typography["body-md"],
            { color: theme.text.secondary, marginTop: spacing.xxs },
          ]}
        >
          Choose at least 3. You can change these later in Settings.
        </Text>
        <Text
          style={[
            typography["caption-uppercase"],
            { color: theme.brand.primary, marginTop: spacing.xxs },
          ]}
        >
          {selected.length} selected
        </Text>
      </View>

      {/* Genre chips */}
      <ScrollView
        contentContainerStyle={[styles.chipGrid, { padding: spacing.sm }]}
        showsVerticalScrollIndicator={false}
      >
        {genres.map((genre) => {
          const active = selected.includes(genre);
          return (
            <TouchableOpacity
              key={genre}
              onPress={() => toggle(genre)}
              activeOpacity={0.75}
              style={[
                styles.chip,
                {
                  backgroundColor: active
                    ? theme.brand.primary
                    : theme.background.elevated,
                  borderRadius: rounded.full,
                  paddingHorizontal: spacing.xs,
                  paddingVertical: spacing.xxs,
                },
              ]}
            >
              <Text
                style={[
                  typography["body-sm"],
                  {
                    color: active ? theme.brand.onPrimary : theme.text.secondary,
                    fontWeight: active ? "600" : "400",
                  },
                ]}
              >
                {genre}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      {/* Footer */}
      <View style={[styles.footer, { paddingHorizontal: spacing.sm, paddingBottom: spacing.sm }]}>
        <TouchableOpacity
          onPress={handleContinue}
          disabled={saving || selected.length < 3}
          activeOpacity={0.8}
          style={[
            styles.continueBtn,
            {
              backgroundColor: theme.brand.primary,
              opacity: saving || selected.length < 3 ? 0.4 : 1,
            },
          ]}
        >
          {saving ? (
            <ActivityIndicator color={theme.brand.onPrimary} />
          ) : (
            <Text style={[typography["button"], { color: theme.brand.onPrimary }]}>
              Continue
            </Text>
          )}
        </TouchableOpacity>

        <View style={[styles.stepRow, { marginTop: spacing.xxs }]}>
          <View style={[styles.stepDot, { backgroundColor: theme.background.elevated }]} />
          <View style={[styles.stepDot, { backgroundColor: theme.brand.primary }]} />
          <View style={[styles.stepDot, { backgroundColor: theme.background.elevated }]} />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: { paddingTop: 16, paddingBottom: 8 },
  chipGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  chip: {
    marginBottom: 0,
  },
  footer: {},
  continueBtn: {
    height: 52,
    alignItems: "center",
    justifyContent: "center",
  },
  stepRow: {
    flexDirection: "row",
    justifyContent: "center",
    gap: 8,
    marginTop: 16,
  },
  stepDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
});