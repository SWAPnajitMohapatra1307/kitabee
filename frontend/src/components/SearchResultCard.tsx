import React from "react";
import { View, Text, Image, Pressable, StyleSheet } from "react-native";
import { useTheme } from "../theme/ThemeContext";
import type { Book } from "../services/books";

type Props = {
  item: Book;
  onPress: () => void;
};

export default function SearchResultCard({ item, onPress }: Props) {
  const { theme, typography, spacing, rounded } = useTheme();

  const sourceLabel =
    item.external_source === "google_books"
      ? "BOOK"
      : item.external_source === "comic_vine"
      ? "COMIC"
      : "FREE";

  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [
        styles.container,
        {
          backgroundColor: theme.background.card,
          padding: spacing.md,
          borderRadius: rounded.none,
          opacity: pressed ? 0.7 : 1,
        },
      ]}
    >
      <View style={styles.coverWrap}>
        {item.cover_url ? (
          <Image
            source={{ uri: item.cover_url }}
            style={styles.cover}
            resizeMode="cover"
          />
        ) : (
          <View
            style={[
              styles.coverFallback,
              { backgroundColor: theme.background.sunken },
            ]}
          >
            <Text style={[typography["title-md"], { color: theme.text.muted }]}>
              {item.title.charAt(0).toUpperCase()}
            </Text>
          </View>
        )}
      </View>

      <View style={{ flex: 1, marginLeft: spacing.md }}>
        <View style={styles.badgeRow}>
          <View
            style={[
              styles.badge,
              { backgroundColor: theme.background.sunken },
            ]}
          >
            <Text
              style={[
                typography["badge-micro"],
                { color: theme.text.secondary },
              ]}
            >
              {sourceLabel}
            </Text>
          </View>
          {item.is_free && (
            <View
              style={[
                styles.badge,
                { backgroundColor: "#FFC93C", marginLeft: spacing.xs },
              ]}
            >
              <Text
                style={[
                  typography["badge-micro"],
                  { color: "#000" },
                ]}
              >
                FREE
              </Text>
            </View>
          )}
        </View>

        <Text
          style={[
            typography["row-title"],
            { color: theme.text.primary, marginTop: spacing.xs },
          ]}
          numberOfLines={2}
        >
          {item.title}
        </Text>

        {item.author && (
          <Text
            style={[
              typography["body-sm"],
              { color: theme.text.secondary, marginTop: 2 },
            ]}
            numberOfLines={1}
          >
            {item.author}
          </Text>
        )}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "flex-start",
  },
  coverWrap: {
    width: 60,
    height: 90,
  },
  cover: {
    width: 60,
    height: 90,
  },
  coverFallback: {
    width: 60,
    height: 90,
    alignItems: "center",
    justifyContent: "center",
  },
  badgeRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  badge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
});