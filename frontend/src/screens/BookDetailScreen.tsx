import React, { useEffect, useState } from "react"
import {
  View,
  Text,
  Image,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Linking,
  StyleSheet,
  Alert,
} from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import { useTheme } from "../theme/ThemeContext"
import { fetchBookById, fetchSimilarBooks, Book } from "../services/books"
import { rateBook, getMyRating } from "../services/ratings"
import { LibraryStatus } from "../services/library"
import { useLibraryStore } from "../stores/libraryStore"
import CollectionRow from "../components/CollectionRow"
import type { ContentSource } from "../services/collections"

const STATUS_OPTIONS: { key: LibraryStatus; label: string }[] = [
  { key: "want_to_read", label: "Want to Read" },
  { key: "currently_reading", label: "Reading" },
  { key: "read", label: "Read" },
  { key: "dnf", label: "DNF" },
]

const BookDetailScreen: React.FC<any> = ({ route, navigation }) => {
  const { content_id } = route.params
  const { theme, typography, spacing, rounded } = useTheme()

  const libraryStore = useLibraryStore()

  const [book, setBook] = useState<Book | null>(null)
  const [loading, setLoading] = useState(true)
  const [similarBooks, setSimilarBooks] = useState<Book[]>([])
  const [userRating, setUserRating] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const libraryItem = libraryStore.getItem(content_id)
  const inLibrary = !!libraryItem
  const currentStatus = libraryItem?.status

  useEffect(() => {
    loadData()
  }, [content_id])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [bookData, similarData, ratingData] = await Promise.all([
        fetchBookById(content_id),
        fetchSimilarBooks(content_id),
        getMyRating(content_id),
      ])

      setBook(bookData)
      setSimilarBooks(similarData)
      setUserRating(ratingData?.rating ?? null)

      if (!libraryStore.loaded) {
        await libraryStore.load()
      }
    } catch (err: any) {
      console.error("Failed to load book:", err)
      setError(
        err?.response?.data?.error?.message ||
          err?.message ||
          "Failed to load book"
      )
    } finally {
      setLoading(false)
    }
  }

  const handleLibraryToggle = async () => {
    try {
      if (inLibrary) {
        await libraryStore.removeFromLibrary(content_id)
      } else {
        await libraryStore.addToLibrary(content_id, "want_to_read")
      }
    } catch (err) {
      Alert.alert("Error", "Could not update library")
    }
  }

  const handleSetStatus = async (status: LibraryStatus) => {
    try {
      await libraryStore.setStatus(content_id, status)
    } catch (err) {
      Alert.alert("Error", "Could not update status")
    }
  }

  const handleRate = async (rating: number) => {
    try {
      await rateBook(content_id, { rating })
      setUserRating(rating)
    } catch (err: any) {
      console.error("Rate error:", err?.response?.data || err?.message)
      const msg =
        err?.response?.data?.error?.message ||
        err?.message ||
        "Could not save rating"
      Alert.alert("Error", msg)
    }
  }

  const handleRead = () => {
    if (book?.free_url) {
      Linking.openURL(book.free_url)
    }
  }

  if (loading) {
    return (
      <SafeAreaView
        style={[
          styles.center,
          { backgroundColor: theme.background.primary },
        ]}
      >
        <ActivityIndicator color={theme.brand.primary} size="large" />
      </SafeAreaView>
    )
  }

  if (error || !book) {
    return (
      <SafeAreaView
        style={[
          styles.center,
          { backgroundColor: theme.background.primary, padding: spacing.sm },
        ]}
      >
        <Text
          style={[
            typography["body-md"],
            { color: theme.text.primary, textAlign: "center" },
          ]}
        >
          {error || "Book not found"}
        </Text>
      </SafeAreaView>
    )
  }

  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: theme.background.primary }}
      edges={["top"]}
    >
      <ScrollView contentContainerStyle={{ paddingBottom: spacing.lg }}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={{ padding: spacing.xs }}
        >
          <Text
            style={[
              typography["title-md"],
              { color: theme.text.primary },
            ]}
          >
            ← Back
          </Text>
        </TouchableOpacity>

        {book.cover_url ? (
          <Image
            source={{ uri: book.cover_url }}
            style={[
              styles.cover,
              {
                borderRadius: rounded.md,
                alignSelf: "center",
                marginTop: spacing.sm,
              },
            ]}
            resizeMode="cover"
          />
        ) : (
          <View
            style={[
              styles.cover,
              {
                borderRadius: rounded.md,
                alignSelf: "center",
                marginTop: spacing.sm,
                backgroundColor: theme.background.elevated,
                alignItems: "center",
                justifyContent: "center",
              },
            ]}
          >
            <Text
              style={[typography["body-md"], { color: theme.text.muted }]}
            >
              No Cover
            </Text>
          </View>
        )}

        <View style={{ paddingHorizontal: spacing.md, marginTop: spacing.md }}>
          <Text
            style={[typography["display-md"], { color: theme.text.primary }]}
          >
            {book.title}
          </Text>
          {book.authors && book.authors.length > 0 && (
            <Text
              style={[
                typography["body-md"],
                { color: theme.text.secondary, marginTop: spacing.xs },
              ]}
            >
              {book.authors.join(", ")}
            </Text>
          )}
        </View>

        <View style={{ paddingHorizontal: spacing.md, marginTop: spacing.md }}>
          <TouchableOpacity
            onPress={handleLibraryToggle}
            style={[
              styles.button,
              {
                backgroundColor: inLibrary
                  ? theme.background.elevated
                  : theme.brand.primary,
                borderRadius: rounded.md,
              },
            ]}
          >
            <Text
              style={[
                typography["title-sm"],
                {
                  color: inLibrary
                    ? theme.text.primary
                    : theme.text.onPrimary,
                  textAlign: "center",
                },
              ]}
            >
              {inLibrary ? "Remove from Library" : "Add to Library"}
            </Text>
          </TouchableOpacity>

          {inLibrary && (
            <View
              style={{
                flexDirection: "row",
                flexWrap: "wrap",
                marginTop: spacing.xs,
              }}
            >
              {STATUS_OPTIONS.map((s) => {
                const active = currentStatus === s.key
                return (
                  <TouchableOpacity
                    key={s.key}
                    onPress={() => handleSetStatus(s.key)}
                    activeOpacity={0.7}
                    style={{
                      paddingHorizontal: spacing.xs,
                      paddingVertical: 6,
                      marginRight: 6,
                      marginTop: 6,
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
                      {s.label}
                    </Text>
                  </TouchableOpacity>
                )
              })}
            </View>
          )}
        </View>

        {book.is_free && book.free_url && (
          <View
            style={{ paddingHorizontal: spacing.md, marginTop: spacing.sm }}
          >
            <TouchableOpacity
              onPress={handleRead}
              style={[
                styles.button,
                {
                  backgroundColor: theme.background.card,
                  borderRadius: rounded.md,
                },
              ]}
            >
              <Text
                style={[
                  typography["title-sm"],
                  { color: theme.text.link, textAlign: "center" },
                ]}
              >
                Read Free on Archive.org
              </Text>
            </TouchableOpacity>
          </View>
        )}

        <View style={{ paddingHorizontal: spacing.md, marginTop: spacing.md }}>
          <Text
            style={[
              typography["title-sm"],
              { color: theme.text.secondary, marginBottom: spacing.xs },
            ]}
          >
            Your Rating
          </Text>
          <View style={{ flexDirection: "row", gap: spacing.xs }}>
            {[1, 2, 3, 4, 5].map((star) => (
              <TouchableOpacity key={star} onPress={() => handleRate(star)}>
                <Text
                  style={{
                    fontSize: 28,
                    color:
                      userRating && star <= userRating
                        ? theme.brand.primary
                        : theme.text.muted,
                  }}
                >
                  ★
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {book.description && (
          <View
            style={{ paddingHorizontal: spacing.md, marginTop: spacing.md }}
          >
            <Text
              style={[typography["body-md"], { color: theme.text.secondary }]}
            >
              {book.description}
            </Text>
          </View>
        )}

        {similarBooks.length > 0 && (
          <View style={{ marginTop: spacing.lg }}>
            <CollectionRow
              collection={{
                id: "similar",
                title: "Similar Books",
                mood: "",
                item_count: similarBooks.length,
                items: similarBooks.map((b) => ({
                  content_id: b.content_id,
                  title: b.title,
                  author: (b.authors && b.authors[0]) || "",
                  cover_url: b.cover_url ?? null,
                  content_type: "book" as const,
                  is_free: b.is_free,
                  free_url: b.free_url ?? null,
                  source: ((b as any).source ?? "google_books") as ContentSource,
                  description: b.description ?? null,
                  genres: (b as any).genres ?? [],
                })),
              }}
              onItemPress={(item) =>
                navigation.push("BookDetail", { content_id: item.content_id })
              }
            />
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  cover: {
    width: 160,
    height: 240,
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
})

export default BookDetailScreen