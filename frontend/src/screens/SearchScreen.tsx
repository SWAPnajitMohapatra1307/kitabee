import React, { useEffect, useMemo, useState } from "react";
import {
  View,
  Text,
  TextInput,
  FlatList,
  ActivityIndicator,
  StyleSheet,
  Keyboard,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useTheme } from "../theme/ThemeContext";
import SearchResultCard from "../components/SearchResultCard";
import { searchBooks, type Book } from "../services/books";

type NavProp = NativeStackNavigationProp<any>;

const DEBOUNCE_MS = 400;

export default function SearchScreen() {
  const { theme, typography, spacing } = useTheme();
  const navigation = useNavigation<NavProp>();

  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");
  const [results, setResults] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  useEffect(() => {
    console.log(
      "[Search] parent routes:",
      navigation.getParent()?.getState()?.routeNames
    );
    console.log(
      "[Search] self routes:",
      navigation.getState()?.routeNames
    );
  }, [navigation]);

  const showEmpty = useMemo(
    () => debounced.length >= 2 && !loading && !error && results.length === 0,
    [debounced, loading, error, results.length]
  );

  const showHint = debounced.length < 2 && !loading;

 const openDetail = (contentId: string) => {
  (navigation as any).navigate("Home", {
    screen: "BookDetail",
    params: { content_id: contentId },
  });
};

  return (
    <SafeAreaView
      style={[styles.safe, { backgroundColor: theme.background.primary }]}
      edges={["top"]}
    >
      <View style={{ paddingHorizontal: spacing.lg, paddingTop: spacing.md }}>
        <Text
          style={[
            typography["display-lg"],
            { color: theme.text.primary },
          ]}
        >
          Search
        </Text>

        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Books, comics, authors..."
          placeholderTextColor={theme.text.placeholder}
          autoCapitalize="none"
          autoCorrect={false}
          returnKeyType="search"
          onSubmitEditing={Keyboard.dismiss}
          style={[
            styles.input,
            typography["body-md"],
            {
              backgroundColor: theme.background.input,
              color: theme.text.primary,
              marginTop: spacing.md,
              paddingHorizontal: spacing.md,
            },
          ]}
        />
      </View>

      {loading && (
        <View style={styles.centered}>
          <ActivityIndicator color={theme.text.primary} />
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

      {!loading && !error && results.length > 0 && (
        <FlatList
          data={results}
          keyExtractor={(item) => item.content_id}
          contentContainerStyle={{
            paddingHorizontal: spacing.lg,
            paddingTop: spacing.md,
            paddingBottom: spacing.xxl,
          }}
          ItemSeparatorComponent={() => <View style={{ height: spacing.sm }} />}
          keyboardShouldPersistTaps="handled"
          renderItem={({ item }) => (
            <SearchResultCard
              item={item}
              onPress={() => openDetail(item.content_id)}
            />
          )}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
  },
  input: {
    height: 48,
  },
  centered: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
});