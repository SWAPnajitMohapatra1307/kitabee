import React, { useEffect, useState } from "react"
import {
  Modal,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  TouchableWithoutFeedback,
  ActivityIndicator,
  Switch,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from "react-native"
import { useTheme } from "../theme/ThemeContext"
import { rateBook, deleteMyRating, RatingInput } from "../services/ratings"

type Props = {
  visible: boolean
  contentId: string
  existingRating: {
    rating: number
    review_title: string | null
    review_text: string | null
    is_spoiler: boolean
  } | null
  onClose: () => void
  onSaved: (rating: number) => void
  onDeleted: () => void
}

const RatingModal: React.FC<Props> = ({
  visible,
  contentId,
  existingRating,
  onClose,
  onSaved,
  onDeleted,
}) => {
  const { theme, typography, spacing, rounded } = useTheme()

  const [stars, setStars] = useState<number>(0)
  const [reviewTitle, setReviewTitle] = useState("")
  const [reviewText, setReviewText] = useState("")
  const [isSpoiler, setIsSpoiler] = useState(false)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (visible) {
      setStars(existingRating?.rating ?? 0)
      setReviewTitle(existingRating?.review_title ?? "")
      setReviewText(existingRating?.review_text ?? "")
      setIsSpoiler(existingRating?.is_spoiler ?? false)
      setError(null)
    }
  }, [visible, existingRating])

  const handleSave = async () => {
    if (stars === 0) {
      setError("Pick at least 1 star.")
      return
    }
    setSaving(true)
    setError(null)
    try {
      const input: RatingInput = {
        rating: stars,
        review_title: reviewTitle.trim() || null,
        review_text: reviewText.trim() || null,
        is_spoiler: isSpoiler,
      }
      await rateBook(contentId, input)
      onSaved(stars)
      onClose()
    } catch (err: any) {
      setError(
        err?.response?.data?.error?.message ||
          err?.message ||
          "Could not save rating."
      )
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    setDeleting(true)
    setError(null)
    try {
      await deleteMyRating(contentId)
      onDeleted()
      onClose()
    } catch (err: any) {
      setError(
        err?.response?.data?.error?.message ||
          err?.message ||
          "Could not delete rating."
      )
    } finally {
      setDeleting(false)
    }
  }

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <TouchableWithoutFeedback onPress={onClose}>
        <View style={styles.backdrop} />
      </TouchableWithoutFeedback>

      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.kavWrapper}
        pointerEvents="box-none"
      >
        <View
          style={[
            styles.sheet,
            {
              backgroundColor: theme.background.sheet,
              borderRadius: rounded.xl,
              padding: spacing.md,
            },
          ]}
        >
          <Text
            style={[
              typography["title-md"],
              { color: theme.text.primary, marginBottom: spacing.sm },
            ]}
          >
            {existingRating ? "Edit Rating" : "Rate this Book"}
          </Text>

          {/* Stars */}
          <View style={styles.starsRow}>
            {[1, 2, 3, 4, 5].map((s) => (
              <TouchableOpacity
                key={s}
                onPress={() => setStars(s)}
                hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
              >
                <Text
                  style={{
                    fontSize: 36,
                    color:
                      s <= stars ? theme.brand.primary : theme.text.muted,
                  }}
                >
                  ★
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Review title */}
          <TextInput
            value={reviewTitle}
            onChangeText={setReviewTitle}
            placeholder="Review title (optional)"
            placeholderTextColor={theme.text.placeholder}
            maxLength={200}
            style={[
              styles.input,
              {
                backgroundColor: theme.background.input,
                borderRadius: rounded.sm,
                color: theme.text.primary,
                padding: spacing.sm,
                marginTop: spacing.sm,
              },
              typography["body-md"] as any,
            ]}
          />

          {/* Review text */}
          <TextInput
            value={reviewText}
            onChangeText={setReviewText}
            placeholder="Write a review (optional)"
            placeholderTextColor={theme.text.placeholder}
            maxLength={5000}
            multiline
            numberOfLines={4}
            style={[
              styles.input,
              styles.multiline,
              {
                backgroundColor: theme.background.input,
                borderRadius: rounded.sm,
                color: theme.text.primary,
                padding: spacing.sm,
                marginTop: spacing.sm,
              },
              typography["body-md"] as any,
            ]}
          />

          {/* Spoiler toggle */}
          <View style={[styles.spoilerRow, { marginTop: spacing.sm }]}>
            <Text
              style={[typography["body-sm"], { color: theme.text.secondary }]}
            >
              Contains spoilers
            </Text>
            <Switch
              value={isSpoiler}
              onValueChange={setIsSpoiler}
              trackColor={{
                false: theme.background.elevated,
                true: theme.brand.primary,
              }}
              thumbColor={theme.text.onPrimary}
            />
          </View>

          {/* Error */}
          {error && (
            <Text
              style={[
                typography["body-sm"],
                { color: theme.brand.semanticWarning, marginTop: spacing.xs },
              ]}
            >
              {error}
            </Text>
          )}

          {/* Buttons */}
          <View style={[styles.buttonRow, { marginTop: spacing.md }]}>
            {existingRating && (
              <TouchableOpacity
                onPress={handleDelete}
                disabled={deleting || saving}
                style={[
                  styles.btn,
                  {
                    backgroundColor: theme.background.elevated,
                    borderRadius: rounded.md,
                    marginRight: spacing.xs,
                  },
                ]}
              >
                {deleting ? (
                  <ActivityIndicator
                    size="small"
                    color={theme.brand.semanticWarning}
                  />
                ) : (
                  <Text
                    style={[
                      typography["title-sm"],
                      {
                        color: theme.brand.semanticWarning,
                        textAlign: "center",
                      },
                    ]}
                  >
                    Delete
                  </Text>
                )}
              </TouchableOpacity>
            )}

            <TouchableOpacity
              onPress={onClose}
              disabled={saving || deleting}
              style={[
                styles.btn,
                {
                  backgroundColor: theme.background.elevated,
                  borderRadius: rounded.md,
                  marginRight: spacing.xs,
                },
              ]}
            >
              <Text
                style={[
                  typography["title-sm"],
                  { color: theme.text.secondary, textAlign: "center" },
                ]}
              >
                Cancel
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleSave}
              disabled={saving || deleting || stars === 0}
              style={[
                styles.btn,
                styles.btnPrimary,
                {
                  backgroundColor:
                    stars === 0
                      ? theme.background.elevated
                      : theme.brand.primary,
                  borderRadius: rounded.md,
                },
              ]}
            >
              {saving ? (
                <ActivityIndicator
                  size="small"
                  color={theme.text.onPrimary}
                />
              ) : (
                <Text
                  style={[
                    typography["title-sm"],
                    {
                      color:
                        stars === 0
                          ? theme.text.muted
                          : theme.text.onPrimary,
                      textAlign: "center",
                    },
                  ]}
                >
                  Save
                </Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  )
}

const styles = StyleSheet.create({
  backdrop: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0,0,0,0.55)",
  },
  kavWrapper: {
    flex: 1,
    justifyContent: "flex-end",
    paddingHorizontal: 16,
    paddingBottom: 32,
  },
  sheet: {
    width: "100%",
  },
  starsRow: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 4,
  },
  input: {
    width: "100%",
  },
  multiline: {
    height: 100,
    textAlignVertical: "top",
  },
  spoilerRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  buttonRow: {
    flexDirection: "row",
    justifyContent: "flex-end",
  },
  btn: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    minWidth: 72,
  },
  btnPrimary: {
    flex: 1,
    maxWidth: 120,
  },
})

export default RatingModal