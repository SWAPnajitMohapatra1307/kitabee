import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  Image,
  StyleSheet,
  SafeAreaView,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useRoute, RouteProp } from "@react-navigation/native";
import { Ionicons } from "@expo/vector-icons";
import { useTheme } from "../../theme/ThemeContext";
import { useUserStore } from "../../stores/userStore";
import { api } from "../../services/api";
import { OnboardingStackParamList } from "../../navigation/OnboardingNavigator";

type Route = RouteProp<OnboardingStackParamList, "RateInitialContent">;

interface SeedItem {
  content_id: string;
  title: string;
  authors: string[];
  cover_url: string | null;
  userRating: number | null;
}

export default function RateInitialContentScreen() {
  const { theme, typography, spacing, rounded } = useTheme();
  const route = useRoute<Route>();
  const { contentType, genres } = route.params;
  const setUser = useUserStore((s) => s.setUser);

  const [items, setItems] = useState<SeedItem[]>([]);
  const [loadingItems, setLoadingItems] = useState(true);
  const [completing, setCompleting] = useState(false);

  const ratedCount = items.filter((i) => i.userRating !== null).length;
  const canFinish = ratedCount >= 3;

  useEffect(() => {
    fetchSeedItems();
  }, []);

  const fetchSeedItems = async () => {
    setLoadingItems(true);
    try {
      const res = await api.get("/search", {
        params: {
          q: genres[0] ?? "fiction",
          limit: 10,
          content_type: contentType === "both" ? undefined : contentType,
        },
      });
      const results: any[] = res.data.data?.results ?? [];
      setItems(
        results.slice(0, 10).map((r: any) => ({
          content_id: r.content_id,
          title: r.title,
          authors: r.authors ?? [],
          cover_url: r.cover_url ?? null,
          userRating: null,
        }))
      );
    } catch {
      // silently fail — user can skip
    } finally {
      setLoadingItems(false);
    }
  };

  const setRating = (content_id: string, rating: number) => {
    setItems((prev) =>
      prev.map((i) =>
        i.content_id === content_id
          ? { ...i, userRating: i.userRating === rating ? null : rating }
          : i
      )
    );
  };

  const submitRatings = async () => {
    const rated = items.filter((i) => i.userRating !== null);
    await Promise.allSettled(
      rated.map((i) =>
        api.post(`/ratings/${i.content_id}`, { rating: i.userRating })
      )
    );
  };

     const handleFinish = async () => {
    setCompleting(true);
    try {
      if (ratedCount > 0) await submitRatings();
      await api.post("/users/me/preferences/complete");
      const meRes = await api.get("/users/me");
      
      const updatedUser = meRes.data?.data ?? meRes.data?.user ?? meRes.data;
      if (updatedUser && typeof updatedUser === "object") {
        setUser({
          ...updatedUser,
          onboarding_completed: true,
        });
      }
    } catch (err: any) {
      console.error("Finish onboarding error:", err);
      Alert.alert("Error", "Something went wrong. Try again.");
      setCompleting(false);
    }
  };
  const renderStars = (item: SeedItem) => (
    <View style={styles.stars}>
      {[1, 2, 3, 4, 5].map((star) => (
        <TouchableOpacity
          key={star}
          onPress={() => setRating(item.content_id, star)}
          activeOpacity={0.7}
          hitSlop={{ top: 8, bottom: 8, left: 4, right: 4 }}
        >
          <Ionicons
            name={item.userRating !== null && star <= item.userRating ? "star" : "star-outline"}
            size={22}
            color={
              item.userRating !== null && star <= item.userRating
                ? theme.brand.primary
                : theme.text.muted
            }
          />
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderItem = ({ item }: { item: SeedItem }) => (
    <View
      style={[
        styles.card,
        {
          backgroundColor: theme.background.elevated,
          borderRadius: rounded.md,
          padding: spacing.xs,
          marginBottom: spacing.xxs,
        },
      ]}
    >
      {item.cover_url ? (
        <Image
          source={{ uri: item.cover_url }}
          style={[styles.cover, { borderRadius: rounded.sm, backgroundColor: theme.background.sunken }]}
        />
      ) : (
        <View style={[styles.cover, { borderRadius: rounded.sm, backgroundColor: theme.background.sunken }]} />
      )}
      <View style={{ flex: 1, marginLeft: spacing.xs, justifyContent: "center" }}>
        <Text
          numberOfLines={2}
          style={[typography["title-sm"], { color: theme.text.primary }]}
        >
          {item.title}
        </Text>
        {item.authors.length > 0 && (
          <Text
            numberOfLines={1}
            style={[typography["body-sm"], { color: theme.text.secondary, marginTop: 2 }]}
          >
            {item.authors.join(", ")}
          </Text>
        )}
        <View style={{ marginTop: 8 }}>{renderStars(item)}</View>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={[styles.root, { backgroundColor: theme.background.primary }]}>
      {/* Header */}
      <View style={[styles.header, { paddingHorizontal: spacing.sm }]}>
        <Text style={[typography["display-md"], { color: theme.text.primary }]}>
          Rate some titles
        </Text>
        <Text
          style={[
            typography["body-md"],
            { color: theme.text.secondary, marginTop: spacing.xxs },
          ]}
        >
          Rate at least 3 to help us personalise your recommendations.
        </Text>
        <Text
          style={[
            typography["caption-uppercase"],
            { color: theme.brand.primary, marginTop: spacing.xxs },
          ]}
        >
          {ratedCount} rated
        </Text>
      </View>

      {/* List */}
      {loadingItems ? (
        <View style={styles.center}>
          <ActivityIndicator color={theme.brand.primary} />
        </View>
      ) : items.length === 0 ? (
        <View style={styles.center}>
          <Text style={[typography["body-md"], { color: theme.text.secondary }]}>
            No titles found. You can skip this step.
          </Text>
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(i) => i.content_id}
          renderItem={renderItem}
          contentContainerStyle={{ padding: spacing.sm }}
        />
      )}

      {/* Footer */}
      <View style={[styles.footer, { paddingHorizontal: spacing.sm, paddingBottom: spacing.sm }]}>
        <TouchableOpacity
          onPress={handleFinish}
          disabled={completing}
          activeOpacity={0.8}
          style={[
            styles.finishBtn,
            {
              backgroundColor: canFinish ? theme.brand.primary : theme.background.elevated,
              opacity: completing ? 0.5 : 1,
            },
          ]}
        >
          {completing ? (
            <ActivityIndicator color={theme.brand.onPrimary} />
          ) : (
            <Text
              style={[
                typography["button"],
                {
                  color: canFinish ? theme.brand.onPrimary : theme.text.muted,
                },
              ]}
            >
              {canFinish ? "Finish Setup" : `Rate ${3 - ratedCount} more to finish`}
            </Text>
          )}
        </TouchableOpacity>

        {!canFinish && (
          <TouchableOpacity
            onPress={handleFinish}
            disabled={completing}
            activeOpacity={0.7}
            style={{ alignItems: "center", marginTop: 12 }}
          >
            <Text style={[typography["body-sm"], { color: theme.text.muted }]}>
              Skip for now
            </Text>
          </TouchableOpacity>
        )}

        <View style={[styles.stepRow, { marginTop: spacing.xxs }]}>
          <View style={[styles.stepDot, { backgroundColor: theme.background.elevated }]} />
          <View style={[styles.stepDot, { backgroundColor: theme.background.elevated }]} />
          <View style={[styles.stepDot, { backgroundColor: theme.brand.primary }]} />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: { paddingTop: 16, paddingBottom: 8 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  card: { flexDirection: "row", alignItems: "center" },
  cover: { width: 60, height: 90 },
  stars: { flexDirection: "row", gap: 4 },
  footer: {},
  finishBtn: {
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