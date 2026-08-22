import React, { useEffect, useState, useCallback } from "react"
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
import {
  fetchBookById,
  fetchSimilarBooks,
  fetchSeriesData,
  Book,
  SeriesResponse,
} from "../services/books"
import { getMyRating, Rating } from "../services/ratings"
import { LibraryStatus } from "../services/library"
import { useLibraryStore } from "../stores/libraryStore"
import CollectionRow from "../components/CollectionRow"
import RatingModal from "../components/RatingModal"
import SeriesOrderSection from "../components/SeriesOrderSection"
import type { ContentSource } from "../services/collections"

const STATUS_OPTIONS: { key: LibraryStatus; label: string }[] = [
  { key: "want_to_read", label: "Want to Read" },
  { key: "currently_reading", label: "Reading" },
  { key: "read", label: "Read" },
  { key: "dnf", label: "DNF" },
]

const BookDetailScreen: React.FC<any> = ({ route, navigation }) => {
  const {
    content_id,
    cover_url: paramCoverUrl = null,
    title: paramTitle = null,
    author: paramAuthor = null,
  } = route.params ?? {}

  const { theme, typography, spacing, rounded } = useTheme()
  const libraryStore = useLibraryStore()

  // Seed from nav params so cover/title paint instantly (often from Home image cache)
  const [book, setBook] = useState<Book | null>(
    paramTitle || paramCoverUrl
      ? ({
          content_id,
          title: paramTitle ?? "",
          authors: paramAuthor ? [paramAuthor] : [],
          cover_url: paramCoverUrl,
        } as Partial<Book> as Book)
      : null
  )
  const [bookLoading, setBookLoading] = useState(!paramTitle && !paramCoverUrl)
  const [similarBooks, setSimilarBooks] = useState<Book[]>([])
  const [seriesData, setSeriesData] = useState<SeriesResponse>(null)
  const [existingRating, setExistingRating] = useState<Rating | null>(null)
  const [ratingModalVisible, setRatingModalVisible] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [coverFailed, setCoverFailed] = useState(false)

  const libraryItem = libraryStore.getItem(content_id)
  const inLibrary = !!libraryItem
  const currentStatus = libraryItem?.status

  // Hero cover: prefer live book data, fall back to param (instant)
  const heroCoverUrl = book?.cover_url || paramCoverUrl || null
  const heroTitle = book?.title || paramTitle || ""
  const heroAuthors =
    book?.authors?.length
      ? book.authors
      : paramAuthor
        ? [paramAuthor]
        : []

  const loadData = useCallback(async (id: string) => {
    setError(null)
    setCoverFailed(false)
    // Only full-block if we have nothing to show yet
    if (!paramTitle && !paramCoverUrl) {
      setBookLoading(true)
    }

    try {
      // 1) Book first — unlock main UI ASAP
      const bookData = await fetchBookById(id)
      setBook(bookData)
      setBookLoading(false)

      if (!libraryStore.loaded) {
        libraryStore.load().catch(() => {})
      }

      // 2) Secondary data in parallel (does not block cover/title)
      const [similarData, ratingData, seriesResult] = await Promise.all([
        fetchSimilarBooks(id).catch(() => []),
        getMyRating(id).catch(() => null),
        fetchSeriesData(id).catch(() => null),
      ])

      setSimilarBooks(similarData || [])
      setExistingRating(ratingData)
      setSeriesData(seriesResult)
    } catch (err: any) {
      console.error("Failed to load book:", err)
      setError(
        err?.response?.data?.error?.message ||
          err?.message ||
          "Failed to load book"
      )
      setBookLoading(false)
    }
  }, [paramTitle, paramCoverUrl])

  useEffect(() => {
    // Reset secondary state when navigating to another book
    setSimilarBooks([])
    setSeriesData(null)
    setExistingRating(null)
    setCoverFailed(false)
    setBook(
      paramTitle || paramCoverUrl
        ? ({
            content_id,
            title: paramTitle ?? "",
            authors: paramAuthor ? [paramAuthor] : [],
            cover_url: paramCoverUrl,
          } as Partial<Book> as Book)
        : null
    )
    loadData(content_id)
  }, [content_id])

  const handleLibraryToggle = async () => {
    try {
      if (inLibrary) {
        await libraryStore.removeFromLibrary(content_id)
      } else {
        await libraryStore.addToLibrary(content_id, "want_to_read")
      }
    } catch {
      Alert.alert("Error", "Could not update library")
    }
  }

  const handleSetStatus = async (status: LibraryStatus) => {
    try {
      await libraryStore.setStatus(content_id, status)
    } catch {
      Alert.alert("Error", "Could not update status")
    }
  }

  const handleRead = () => {
    if (book?.free_url) Linking.openURL(book.free_url)
  }

  const handleRatingSaved = (newStars: number) => {
    setExistingRating((prev) =>
      prev
        ? { ...prev, rating: newStars }
        : ({
            id: "",
            user_id: "",
            book_id: "",
            rating: newStars,
            review_title: null,
            review_text: null,
            is_spoiler: false,
            helpful_count: 0,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          } as Rating)
    )
  }

  // Only block entire screen if we have no params AND book hasn't loaded
  if (bookLoading && !book && !paramCoverUrl) {
    return (
      <SafeAreaView
        style={[styles.center, { backgroundColor: theme.background.primary }]}
      >
        <ActivityIndicator color={theme.brand.primary} size="large" />
      </SafeAreaView>
    )
  }

  if ((error && !book) || (!book && !paramCoverUrl && !bookLoading)) {
    return (
      <SafeAreaView
        style={[
          styles.center,
          { backgroundColor: theme.background.primary, padding: spacing.sm },
        ]}
      >
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={{ position: "absolute", top: spacing.lg, left: spacing.md }}
        >
          <Text style={[typography["title-md"], { color: theme.text.primary }]}>
            ← Back
          </Text>
        </TouchableOpacity>
        <Text
          style={[
            typography["body-md"],
            { color: theme.text.primary, textAlign: "center" },
          ]}
        >
          {error || "Book not found"}
        </Text>
        <TouchableOpacity
          onPress={() => loadData(content_id)}
          style={{
            marginTop: spacing.md,
            paddingVertical: spacing.xs,
            paddingHorizontal: spacing.md,
            backgroundColor: theme.brand.primary,
            borderRadius: rounded.md,
          }}
        >
          <Text style={[typography["title-sm"], { color: theme.text.onPrimary }]}>
            Retry
          </Text>
        </TouchableOpacity>
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
          <Text style={[typography["title-md"], { color: theme.text.primary }]}>
            ← Back
          </Text>
        </TouchableOpacity>

       {/* Hero Cover Image in BookDetailScreen.tsx */}
{heroCoverUrl && !coverFailed ? (
  <Image
    source={{ uri: heroCoverUrl }}
    style={[
      styles.cover,
      {
        borderRadius: rounded.md,
        alignSelf: "center",
        marginTop: spacing.sm,
        backgroundColor: theme.background.elevated,
      },
    ]}
    resizeMode="cover"
    onError={() => setCoverFailed(true)}
  />
) : (
  /* Elegant Book Cover Placeholder when image is missing or 404s */
  <View
    style={[
      styles.cover,
      {
        borderRadius: rounded.md,
        alignSelf: "center",
        marginTop: spacing.sm,
        backgroundColor: theme.brand.primary,
        alignItems: "center",
        justifyContent: "center",
        padding: spacing.sm,
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 5,
        elevation: 6,
      },
    ]}
  >
    <Text
      style={[
        typography["title-md"],
        { color: theme.brand.onPrimary, textAlign: "center" },
      ]}
      numberOfLines={3}
    >
      {heroTitle || "Kitabee"}
    </Text>
    {heroAuthors.length > 0 && (
      <Text
        style={[
          typography["caption-uppercase"],
          { color: theme.brand.onPrimary, textAlign: "center", marginTop: 8, opacity: 0.8 },
        ]}
        numberOfLines={1}
      >
        {heroAuthors[0]}
      </Text>
    )}
  </View>
)}

        <View style={{ paddingHorizontal: spacing.md, marginTop: spacing.md }}>
          <Text style={[typography["display-md"], { color: theme.text.primary }]}>
            {heroTitle || "Loading…"}
          </Text>
          {heroAuthors.length > 0 && (
            <Text
              style={[
                typography["body-md"],
                { color: theme.text.secondary, marginTop: spacing.xs },
              ]}
            >
              {heroAuthors.join(", ")}
            </Text>
          )}
        </View>

        {/* Library / rating / description only when full book is in */}
        {book && book.title ? (
          <>
            <View
              style={{ paddingHorizontal: spacing.md, marginTop: spacing.md }}
            >
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
                style={{
                  paddingHorizontal: spacing.md,
                  marginTop: spacing.sm,
                }}
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

            <View
              style={{ paddingHorizontal: spacing.md, marginTop: spacing.md }}
            >
              <Text
                style={[
                  typography["title-sm"],
                  { color: theme.text.secondary, marginBottom: spacing.xs },
                ]}
              >
                Your Rating
              </Text>

              {existingRating ? (
                <View
                  style={{
                    flexDirection: "row",
                    alignItems: "center",
                    gap: spacing.sm,
                  }}
                >
                  <View style={{ flexDirection: "row", gap: 4 }}>
                    {[1, 2, 3, 4, 5].map((s) => (
                      <Text
                        key={s}
                        style={{
                          fontSize: 24,
                          color:
                            s <= existingRating.rating
                              ? theme.brand.primary
                              : theme.text.muted,
                        }}
                      >
                        ★
                      </Text>
                    ))}
                  </View>
                  <TouchableOpacity onPress={() => setRatingModalVisible(true)}>
                    <Text
                      style={[typography["body-sm"], { color: theme.text.link }]}
                    >
                      Edit
                    </Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <TouchableOpacity
                  onPress={() => setRatingModalVisible(true)}
                  style={[
                    styles.button,
                    {
                      backgroundColor: theme.background.elevated,
                      borderRadius: rounded.md,
                    },
                  ]}
                >
                  <Text
                    style={[
                      typography["title-sm"],
                      { color: theme.text.secondary, textAlign: "center" },
                    ]}
                  >
                    Rate this Book
                  </Text>
                </TouchableOpacity>
              )}
            </View>

            {book.description ? (
              <View
                style={{
                  paddingHorizontal: spacing.md,
                  marginTop: spacing.md,
                }}
              >
                <Text
                  style={[
                    typography["body-md"],
                    { color: theme.text.secondary },
                  ]}
                >
                  {book.description}
                </Text>
              </View>
            ) : null}

            {seriesData && (
              <SeriesOrderSection
                series={seriesData}
                currentContentId={content_id}
                onItemPress={(id) =>
                  navigation.push("BookDetail", { content_id: id })
                }
              />
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
                      author:
                        b.author || (b.authors && b.authors[0]) || "",
                      cover_url: b.cover_url ?? null,
                      content_type:
                        b.content_type === "comic" ? "comic" : "book",
                      is_free: !!b.is_free,
                      free_url: b.free_url ?? null,
                      source: (b.source ||
                        (b as any).external_source ||
                        "google_books") as ContentSource,
                      description: b.description ?? null,
                      genres: b.genres ?? [],
                    })),
                  }}
                  onItemPress={(item) =>
                    navigation.push("BookDetail", {
                      content_id: item.content_id,
                      cover_url: item.cover_url ?? null,
                      title: item.title ?? null,
                      author: item.author ?? null,
                    })
                  }
                />
              </View>
            )}
          </>
        ) : (
          // Soft loading under the already-visible cover
          <View style={{ paddingVertical: spacing.lg, alignItems: "center" }}>
            <ActivityIndicator color={theme.brand.primary} />
          </View>
        )}
      </ScrollView>

      <RatingModal
        visible={ratingModalVisible}
        contentId={content_id}
        existingRating={existingRating}
        onClose={() => setRatingModalVisible(false)}
        onSaved={handleRatingSaved}
        onDeleted={() => setExistingRating(null)}
      />
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