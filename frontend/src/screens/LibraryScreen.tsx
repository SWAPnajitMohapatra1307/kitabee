import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  View,
  Text,
  FlatList,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  StyleSheet,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useNavigation, useFocusEffect } from "@react-navigation/native";
import { Ionicons } from "@expo/vector-icons";
import { useTheme } from "../theme/ThemeContext";
import { LibraryItem, LibraryStatus } from "../services/library";
import { useLibraryStore } from "../stores/libraryStore";
import LibraryEditSheet from "../components/LibraryEditSheet";

type FilterKey = "all" | LibraryStatus;

const FILTERS: { key: FilterKey; label: string }[] = [
  { key: "all", label: "All" },
  { key: "want_to_read", label: "Want" },
  { key: "currently_reading", label: "Reading" },
  { key: "read", label: "Read" },
  { key: "dnf", label: "DNF" },
];

const STATUS_LABELS: Record<LibraryStatus, string> = {
  want_to_read: "Want to Read",
  currently_reading: "Reading",
  read: "Finished",
  dnf: "Dropped",
};

const LibraryScreen: React.FC = () => {
  const { theme, typography, spacing, rounded } = useTheme();
  const navigation = useNavigation<any>();

  const items = useLibraryStore((s) => s.items);
  const loaded = useLibraryStore((s) => s.loaded);
  const loading = useLibraryStore((s) => s.loading);
  const load = useLibraryStore((s) => s.load);
  const syncFromServer = useLibraryStore((s) => s.syncFromServer);

  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterKey>("all");
  const [editing, setEditing] = useState<LibraryItem | null>(null);

  useEffect(() => {
    if (!loaded) {
      load().catch((e) => setError(e?.message || "Failed to load library"));
    }
  }, [loaded, load]);

  useFocusEffect(
    useCallback(() => {
      syncFromServer().catch((e) =>
        setError(e?.message || "Failed to refresh library"),
      );
    }, [syncFromServer]),
  );

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      setError(null);
      await syncFromServer();
    } catch (e: any) {
      setError(e?.message || "Failed to refresh library");
    } finally {
      setRefreshing(false);
    }
  };

  const filteredItems = useMemo(() => {
    if (filter === "all") return items;
    return items.filter((i) => i.status === filter);
  }, [items, filter]);

  // Pass cached cover, title, and author to BookDetail for instant hero paint
  const openDetail = (item: LibraryItem) => {
    const authorName = item.authors && item.authors.length > 0 ? item.authors[0] : null;

    navigation.navigate("Home", {
      screen: "BookDetail",
      params: {
        content_id: item.content_id,
        cover_url: item.cover_url ?? null,
        title: item.title ?? null,
        author: authorName ?? null,
      },
    });
  };

  const renderItem = ({ item }: { item: LibraryItem }) => (
    <TouchableOpacity
      activeOpacity={0.75}
      onPress={() => openDetail(item)}
      onLongPress={() => setEditing(item)}
      delayLongPress={300}
      style={{
        flexDirection: "row",
        padding: spacing.xs,
        marginBottom: spacing.xxs,
        backgroundColor: theme.background.elevated,
        borderRadius: rounded.md,
        alignItems: "center",
      }}
    >
      {item.cover_url ? (
        <Image
          source={{ uri: item.cover_url }}
          style={{
            width: 60,
            height: 90,
            borderRadius: rounded.sm,
            backgroundColor: theme.background.sunken,
          }}
        />
      ) : (
        <View
          style={{
            width: 60,
            height: 90,
            borderRadius: rounded.sm,
            backgroundColor: theme.background.sunken,
          }}
        />
      )}

      <View
        style={{
          flex: 1,
          marginLeft: spacing.xs,
          justifyContent: "center",
        }}
      >
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            gap: 6,
          }}
        >
          <Text
            numberOfLines={2}
            style={[
              typography["title-sm"],
              { color: theme.text.primary, flexShrink: 1 },
            ]}
          >
            {item.title || "Untitled"}
          </Text>
          {item.is_favorite && (
            <Ionicons name="heart" size={14} color={theme.brand.primary} />
          )}
        </View>

        {item.authors && item.authors.length > 0 && (
          <Text
            numberOfLines={1}
            style={[
              typography["body-sm"],
              { color: theme.text.secondary, marginTop: 2 },
            ]}
          >
            {item.authors.join(", ")}
          </Text>
        )}

        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            marginTop: 4,
            gap: 8,
          }}
        >
          <Text
            style={[
              typography["caption-uppercase"],
              { color: theme.text.muted },
            ]}
          >
            {STATUS_LABELS[item.status]}
          </Text>
          {item.status === "currently_reading" &&
            item.current_page != null &&
            item.total_pages != null && (
              <Text
                style={[
                  typography["caption-uppercase"],
                  { color: theme.brand.primary },
                ]}
              >
                {Math.round((item.current_page / item.total_pages) * 100)}%
              </Text>
            )}
        </View>
      </View>

      <TouchableOpacity
        onPress={() => setEditing(item)}
        activeOpacity={0.6}
        hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
        style={{
          padding: 8,
          marginLeft: 4,
        }}
      >
        <Ionicons
          name="ellipsis-vertical"
          size={20}
          color={theme.text.muted}
        />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  const showFullLoader = loading && !loaded;

  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: theme.background.primary }}
    >
      <View
        style={{
          paddingHorizontal: spacing.sm,
          paddingTop: spacing.xs,
          paddingBottom: spacing.xxs,
        }}
      >
        <Text
          style={[typography["display-md"], { color: theme.text.primary }]}
        >
          My Library
        </Text>
      </View>

      <View
        style={{
          flexDirection: "row",
          paddingHorizontal: spacing.sm,
          paddingBottom: spacing.xs,
          flexWrap: "wrap",
        }}
      >
        {FILTERS.map((f) => {
          const active = filter === f.key;
          return (
            <TouchableOpacity
              key={f.key}
              onPress={() => setFilter(f.key)}
              activeOpacity={0.7}
              style={{
                paddingHorizontal: spacing.xs,
                paddingVertical: 4,
                marginRight: 6,
                marginBottom: 6,
                borderRadius: rounded.full,
                backgroundColor: active
                  ? theme.brand.primary
                  : theme.background.elevated,
              }}
            >
              <Text
                style={[
                  typography["caption-uppercase"],
                  {
                    color: active
                      ? theme.text.onPrimary
                      : theme.text.secondary,
                  },
                ]}
              >
                {f.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {showFullLoader ? (
        <View style={styles.center}>
          <ActivityIndicator color={theme.brand.primary} />
        </View>
      ) : error && items.length === 0 ? (
        <View style={styles.center}>
          <Text
            style={[typography["body-md"], { color: theme.text.secondary }]}
          >
            {error}
          </Text>
        </View>
      ) : (
        <FlatList
          data={filteredItems}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={{ padding: spacing.xs }}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListEmptyComponent={
            <View style={styles.center}>
              <Text
                style={[
                  typography["body-md"],
                  { color: theme.text.secondary },
                ]}
              >
                Nothing in this shelf yet.
              </Text>
            </View>
          }
        />
      )}

      <LibraryEditSheet
        visible={editing !== null}
        item={editing}
        onClose={() => setEditing(null)}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
});

export default LibraryScreen;