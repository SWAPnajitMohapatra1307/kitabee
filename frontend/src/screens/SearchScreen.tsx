import React, { useEffect, useMemo, useState } from "react";
import {
  View,
  Text,
  TextInput,
  FlatList,
  ActivityIndicator,
  StyleSheet,
  Keyboard,
  TouchableOpacity,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { useTheme } from "../theme/ThemeContext";
import SearchResultCard from "../components/SearchResultCard";
import { searchBooks, type Book } from "../services/books";

type NavProp = NativeStackNavigationProp<any>;
type ContentFilter = "all" | "books" | "comics";

const DEBOUNCE_MS = 400;

const CONTENT_TABS: { key: ContentFilter; label: string }[] = [
  { key: "all", label: "All" },
  { key: "books", label: "Books" },
  { key: "comics", label: "Comics" },
];

export default function SearchScreen() {
  const { theme, typography, spacing, rounded } = useTheme();
  const navigation = useNavigation<NavProp>();

  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");
  const [contentFilter, setContentFilter] = useState<ContentFilter>("all");
  const [freeOnly, setFreeOnly] = useState(false);
  const [results, setResults] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [focused, setFocused] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(query.trim()), DEBOUNCE_MS);
    return () => clearTimeout(t);
  }, [query]);

  useEffect(() => {
    if (debounced.length < 2) {
      setResults([]);
      setError(null);
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);

    searchBooks(debounced, 20)
      .then((data: Book[]) => {
        if (cancelled) return;
        setResults(data);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        console.error("[Search]", err);
        setError("Search failed. Try again.");
        setResults([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [debounced]);

  const filteredResults = useMemo(() => {
    let out = results;

    if (contentFilter === "books") {
      out = out.filter((r) => r.content_type === "book");
    } else if (contentFilter === "comics") {
      out = out.filter((r) => r.content_type === "comic");
    }

    if (freeOnly) {
      out = out.filter((r) => r.is_free);
    }

    return out;
  }, [results, contentFilter, freeOnly]);

  const showEmpty =
    debounced.length >= 2 && !loading && !error && filteredResults.length === 0;
  const showHint = debounced.length < 2 && !loading;

  // ✅ Pass cached cover, title, and author to BookDetail for instant hero paint
  const openDetail = (item: Book) => {
    const authorName = item.author || (item.authors && item.authors[0]) || null;

    (navigation as any).navigate("Home", {
      screen: "BookDetail",
      params: {
        content_id: item.content_id,
        cover_url: item.cover_url ?? null,
        title: item.title ?? null,
        author: authorName ?? null,
      },
    });
  };

  return (
    <SafeAreaView
      style={[styles.safe, { backgroundColor: theme.background.primary }]}
      edges={["top"]}
    >
      <View style={{ paddingHorizontal: spacing.sm, paddingTop: spacing.sm }}>
        {/* Title */}
        <Text style={[typography["display-lg"], { color: theme.text.primary }]}>
          Search
        </Text>

        {/* Search input with icon */}
        <View
          style={[
            styles.inputWrap,
            {
              backgroundColor: theme.background.input,
              borderColor: focused
                ? theme.brand.primary
                : theme.border.default,
              borderRadius: rounded.sm,
              marginTop: spacing.sm,
            },
          ]}
        >
          <Ionicons
            name="search-outline"
            size={20}
            color={theme.text.muted}
            style={{ marginHorizontal: 12 }}
          />
          <TextInput
            value={query}
            onChangeText={setQuery}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Books, comics, authors..."
            placeholderTextColor={theme.text.placeholder}
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="search"
            onSubmitEditing={Keyboard.dismiss}
            style={[
              styles.input,
              typography["body-md"],
              { color: theme.text.primary },
            ]}
          />
          {query.length > 0 && (
            <TouchableOpacity
              onPress={() => setQuery("")}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              style={{ paddingHorizontal: 12 }}
            >
              <Ionicons name="close-circle" size={18} color={theme.text.muted} />
            </TouchableOpacity>
          )}
        </View>

        {/* Content type tabs */}
        <View style={[styles.tabsRow, { marginTop: spacing.sm }]}>
          {CONTENT_TABS.map((tab) => {
            const active = contentFilter === tab.key;
            return (
              <TouchableOpacity
                key={tab.key}
                onPress={() => setContentFilter(tab.key)}
                activeOpacity={0.7}
                style={styles.tabBtn}
              >
                <Text
                  style={[
                    typography["title-sm"],
                    {
                      color: active ? theme.text.primary : theme.text.muted,
                      fontWeight: active ? "700" : "500",
                    },
                  ]}
                >
                  {tab.label}
                </Text>
                <View
                  style={{
                    height: 2,
                    width: "100%",
                    backgroundColor: active
                      ? theme.brand.primary
                      : "transparent",
                    marginTop: 6,
                  }}
                />
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Free only toggle */}
        <View style={[styles.filterRow, { marginTop: spacing.xs }]}>
          <TouchableOpacity
            onPress={() => setFreeOnly((v) => !v)}
            activeOpacity={0.7}
            style={[
              styles.filterChip,
              {
                backgroundColor: freeOnly
                  ? theme.brand.primary
                  : theme.background.elevated,
                borderRadius: rounded.full,
              },
            ]}
          >
            <Ionicons
              name={freeOnly ? "checkbox" : "square-outline"}
              size={14}
              color={freeOnly ? theme.brand.onPrimary : theme.text.secondary}
              style={{ marginRight: 6 }}
            />
            <Text
              style={[
                typography["caption-uppercase"],
                {
                  color: freeOnly
                    ? theme.brand.onPrimary
                    : theme.text.secondary,
                },
              ]}
            >
              Free only
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {loading && (
        <View style={styles.centered}>
          <ActivityIndicator color={theme.brand.primary} />
        </View>
      )}

      {error && (
        <View style={styles.centered}>
          <Text style={[typography["body-md"], { color: theme.text.muted }]}>
            {error}
          </Text>
        </View>
      )}

      {showEmpty && (
        <View style={styles.centered}>
          <Text style={[typography["body-md"], { color: theme.text.muted }]}>
            No results for "{debounced}"
          </Text>
        </View>
      )}

      {showHint && (
        <View style={styles.centered}>
          <Text style={[typography["body-md"], { color: theme.text.muted }]}>
            Type at least 2 characters
          </Text>
        </View>
      )}

      {!loading && !error && filteredResults.length > 0 && (
        <FlatList
          data={filteredResults}
          keyExtractor={(item) => item.content_id}
          contentContainerStyle={{
            paddingHorizontal: spacing.sm,
            paddingTop: spacing.sm,
            paddingBottom: spacing.xxl,
          }}
          ItemSeparatorComponent={() => <View style={{ height: spacing.xs }} />}
          keyboardShouldPersistTaps="handled"
          renderItem={({ item }) => (
            <SearchResultCard
              item={item}
              onPress={() => openDetail(item)}
            />
          )}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  inputWrap: {
    flexDirection: "row",
    alignItems: "center",
    height: 48,
    borderWidth: 1,
  },
  input: {
    flex: 1,
    height: "100%",
  },
  tabsRow: {
    flexDirection: "row",
    gap: 24,
  },
  tabBtn: {
    alignItems: "center",
    paddingBottom: 4,
  },
  filterRow: {
    flexDirection: "row",
    gap: 8,
  },
  filterChip: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  centered: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
});