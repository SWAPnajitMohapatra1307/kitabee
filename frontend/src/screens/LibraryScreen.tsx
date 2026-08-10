import React, { useCallback, useEffect, useState } from "react"
import {
  View,
  Text,
  FlatList,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  StyleSheet,
} from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import { useNavigation, useFocusEffect } from "@react-navigation/native"
import { useTheme } from "../theme/ThemeContext"
import {
  getMyLibrary,
  LibraryItem,
  LibraryStatus,
} from "../services/library"

type FilterKey = "all" | LibraryStatus

const FILTERS: { key: FilterKey; label: string }[] = [
  { key: "all", label: "All" },
  { key: "want_to_read", label: "Want to Read" },
  { key: "currently_reading", label: "Reading" },
  { key: "read", label: "Read" },
  { key: "dnf", label: "DNF" },
]

const LibraryScreen: React.FC = () => {
  const { theme, typography, spacing, rounded } = useTheme()
  const navigation = useNavigation<any>()

  const [items, setItems] = useState<LibraryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<FilterKey>("all")

  const load = useCallback(async () => {
    try {
      setError(null)
      const statusParam = filter === "all" ? undefined : filter
      const response = await getMyLibrary(statusParam, 100, 0)
      setItems(response.results)
    } catch (err: any) {
      setError(err?.message || "Failed to load library")
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [filter])

  useEffect(() => {
    setLoading(true)
    load()
  }, [load])

  useFocusEffect(
    useCallback(() => {
      load()
    }, [load])
  )

  const onRefresh = () => {
    setRefreshing(true)
    load()
  }

  const renderItem = ({ item }: { item: LibraryItem }) => (
    <TouchableOpacity
      activeOpacity={0.75}
      onPress={() =>
        navigation.navigate("Home", {
          screen: "BookDetail",
          params: { content_id: item.content_id },
        })
      }
      style={{
        flexDirection: "row",
        padding: spacing.xs,
        marginBottom: spacing.xxs,
        backgroundColor: theme.background.elevated,
        borderRadius: rounded.md,
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

      <View style={{ flex: 1, marginLeft: spacing.xs, justifyContent: "center" }}>
        <Text
          numberOfLines={2}
          style={[typography["title-sm"], { color: theme.text.primary }]}
        >
          {item.title || "Untitled"}
        </Text>
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
        <Text
          style={[
            typography["caption-uppercase"],
            { color: theme.text.muted, marginTop: 4 },
          ]}
        >
          {item.status.replace(/_/g, " ")}
        </Text>
      </View>
    </TouchableOpacity>
  )

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
          const active = filter === f.key
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
                    color: active ? theme.text.onPrimary : theme.text.secondary,
                  },
                ]}
              >
                {f.label}
              </Text>
            </TouchableOpacity>
          )
        })}
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator color={theme.brand.primary} />
        </View>
      ) : error ? (
        <View style={styles.center}>
          <Text style={[typography["body-md"], { color: theme.text.secondary }]}>
            {error}
          </Text>
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={{ padding: spacing.xs }}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListEmptyComponent={
            <View style={styles.center}>
              <Text
                style={[typography["body-md"], { color: theme.text.secondary }]}
              >
                Nothing in this shelf yet.
              </Text>
            </View>
          }
        />
      )}
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
})

export default LibraryScreen