import React, { useEffect, useState } from "react";
import {
  Modal,
  View,
  Text,
  TouchableOpacity,
  TextInput,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useTheme } from "../theme/ThemeContext";
import { useLibraryStore } from "../stores/libraryStore";
import { LibraryItem, LibraryStatus } from "../services/library";

interface LibraryEditSheetProps {
  visible: boolean;
  item: LibraryItem | null;
  onClose: () => void;
}

const STATUS_OPTIONS: { key: LibraryStatus; label: string }[] = [
  { key: "want_to_read", label: "Want to Read" },
  { key: "currently_reading", label: "Reading" },
  { key: "read", label: "Finished" },
  { key: "dnf", label: "Dropped" },
];

export default function LibraryEditSheet({
  visible,
  item,
  onClose,
}: LibraryEditSheetProps) {
  const { theme, typography, spacing, rounded } = useTheme();
  const updateEntry = useLibraryStore((s) => s.updateEntry);
  const removeFromLibrary = useLibraryStore((s) => s.removeFromLibrary);

  const [status, setStatus] = useState<LibraryStatus>("want_to_read");
  const [isFavorite, setIsFavorite] = useState(false);
  const [notes, setNotes] = useState("");
  const [currentPage, setCurrentPage] = useState("");
  const [totalPages, setTotalPages] = useState("");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (item) {
      setStatus(item.status);
      setIsFavorite(item.is_favorite);
      setNotes(item.notes ?? "");
      setCurrentPage(item.current_page ? String(item.current_page) : "");
      setTotalPages(item.total_pages ? String(item.total_pages) : "");
    }
  }, [item]);

  if (!item) return null;

  const handleSave = async () => {
    setSaving(true);
    try {
      const updates: any = {
        status,
        is_favorite: isFavorite,
        notes: notes.trim() ? notes.trim() : null,
      };

      const cp = parseInt(currentPage, 10);
      const tp = parseInt(totalPages, 10);
      if (!isNaN(cp) && cp >= 0) updates.current_page = cp;
      if (!isNaN(tp) && tp >= 1) updates.total_pages = tp;

      await updateEntry(item.content_id, updates);
      onClose();
    } catch (err: any) {
      Alert.alert(
        "Error",
        err?.response?.data?.detail?.message ?? "Failed to save changes.",
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = () => {
    Alert.alert(
      "Remove from library?",
      `"${item.title || "This item"}" will be removed from your library. This cannot be undone.`,
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Remove",
          style: "destructive",
          onPress: async () => {
            setDeleting(true);
            try {
              await removeFromLibrary(item.content_id);
              onClose();
            } catch (err: any) {
              Alert.alert("Error", "Failed to remove item.");
              setDeleting(false);
            }
          },
        },
      ],
    );
  };

  const isReading = status === "currently_reading";
  const busy = saving || deleting;

  const progressPct =
    currentPage.length > 0 &&
    totalPages.length > 0 &&
    parseInt(totalPages, 10) > 0
      ? Math.min(
          100,
          (parseInt(currentPage, 10) / parseInt(totalPages, 10)) * 100,
        )
      : null;

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={styles.overlay}
      >
        <TouchableOpacity
          style={styles.overlayTap}
          activeOpacity={1}
          onPress={onClose}
        />

        <View
          style={[
            styles.sheet,
            {
              backgroundColor: theme.background.sheet,
              borderTopLeftRadius: rounded.lg,
              borderTopRightRadius: rounded.lg,
            },
          ]}
        >
          {/* Handle */}
          <View style={styles.handleWrap}>
            <View
              style={[styles.handle, { backgroundColor: theme.text.muted }]}
            />
          </View>

          {/* Header */}
          <View style={[styles.header, { paddingHorizontal: spacing.lg }]}>
            <View style={{ flex: 1 }}>
              <Text
                style={[typography["title-md"], { color: theme.text.primary }]}
                numberOfLines={2}
              >
                {item.title || "Untitled"}
              </Text>
              {item.authors && item.authors.length > 0 && (
                <Text
                  style={[
                    typography["body-sm"],
                    { color: theme.text.secondary, marginTop: 2 },
                  ]}
                  numberOfLines={1}
                >
                  {item.authors.join(", ")}
                </Text>
              )}
            </View>
            <TouchableOpacity
              onPress={onClose}
              activeOpacity={0.7}
              disabled={busy}
              style={{ padding: 4 }}
            >
              <Ionicons name="close" size={24} color={theme.text.secondary} />
            </TouchableOpacity>
          </View>

          <ScrollView
            contentContainerStyle={{
              padding: spacing.lg,
              paddingBottom: spacing.xl,
              gap: spacing.md,
            }}
            keyboardShouldPersistTaps="handled"
          >
            {/* Status picker */}
            <View style={{ gap: spacing.xs }}>
              <Text
                style={[
                  typography["caption-uppercase"],
                  { color: theme.text.muted },
                ]}
              >
                Status
              </Text>
              <View style={styles.statusWrap}>
                {STATUS_OPTIONS.map((opt) => {
                  const active = status === opt.key;
                  return (
                    <TouchableOpacity
                      key={opt.key}
                      onPress={() => setStatus(opt.key)}
                      activeOpacity={0.7}
                      disabled={busy}
                      style={{
                        paddingHorizontal: 14,
                        paddingVertical: 8,
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
                              ? theme.brand.onPrimary
                              : theme.text.secondary,
                          },
                        ]}
                      >
                        {opt.label}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>

            {/* Favorite */}
            <View style={{ gap: spacing.xs }}>
              <Text
                style={[
                  typography["caption-uppercase"],
                  { color: theme.text.muted },
                ]}
              >
                Favorite
              </Text>
              <TouchableOpacity
                onPress={() => setIsFavorite(!isFavorite)}
                activeOpacity={0.7}
                disabled={busy}
                style={[
                  styles.favRow,
                  {
                    backgroundColor: theme.background.elevated,
                    borderRadius: rounded.md,
                    padding: spacing.sm,
                  },
                ]}
              >
                <Ionicons
                  name={isFavorite ? "heart" : "heart-outline"}
                  size={24}
                  color={
                    isFavorite ? theme.brand.primary : theme.text.secondary
                  }
                />
                <Text
                  style={[
                    typography["body-md"],
                    { color: theme.text.primary, marginLeft: spacing.xs },
                  ]}
                >
                  {isFavorite ? "Marked as favorite" : "Mark as favorite"}
                </Text>
              </TouchableOpacity>
            </View>

            {/* Progress (only when reading) */}
            {isReading && (
              <View style={{ gap: spacing.xs }}>
                <Text
                  style={[
                    typography["caption-uppercase"],
                    { color: theme.text.muted },
                  ]}
                >
                  Reading Progress
                </Text>
                <View style={styles.pageRow}>
                  <View style={{ flex: 1 }}>
                    <Text
                      style={[
                        typography["body-sm"],
                        { color: theme.text.secondary, marginBottom: 4 },
                      ]}
                    >
                      Current page
                    </Text>
                    <TextInput
                      value={currentPage}
                      onChangeText={setCurrentPage}
                      keyboardType="number-pad"
                      placeholder="0"
                      placeholderTextColor={theme.text.placeholder}
                      editable={!busy}
                      style={[
                        typography["body-md"],
                        styles.input,
                        {
                          color: theme.text.primary,
                          backgroundColor: theme.background.input,
                          borderColor: theme.border.default,
                          borderRadius: rounded.sm,
                        },
                      ]}
                    />
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text
                      style={[
                        typography["body-sm"],
                        { color: theme.text.secondary, marginBottom: 4 },
                      ]}
                    >
                      Total pages
                    </Text>
                    <TextInput
                      value={totalPages}
                      onChangeText={setTotalPages}
                      keyboardType="number-pad"
                      placeholder="—"
                      placeholderTextColor={theme.text.placeholder}
                      editable={!busy}
                      style={[
                        typography["body-md"],
                        styles.input,
                        {
                          color: theme.text.primary,
                          backgroundColor: theme.background.input,
                          borderColor: theme.border.default,
                          borderRadius: rounded.sm,
                        },
                      ]}
                    />
                  </View>
                </View>

                {progressPct !== null && (
                  <View
                    style={[
                      styles.progressTrack,
                      {
                        backgroundColor: theme.background.sunken,
                        borderRadius: rounded.full,
                      },
                    ]}
                  >
                    <View
                      style={{
                        height: "100%",
                        width: `${progressPct}%`,
                        backgroundColor: theme.brand.primary,
                        borderRadius: rounded.full,
                      }}
                    />
                  </View>
                )}
              </View>
            )}

            {/* Notes */}
            <View style={{ gap: spacing.xs }}>
              <Text
                style={[
                  typography["caption-uppercase"],
                  { color: theme.text.muted },
                ]}
              >
                Notes
              </Text>
              <TextInput
                value={notes}
                onChangeText={setNotes}
                multiline
                numberOfLines={4}
                maxLength={5000}
                placeholder="Your thoughts, quotes, reminders..."
                placeholderTextColor={theme.text.placeholder}
                editable={!busy}
                style={[
                  typography["body-md"],
                  styles.notesInput,
                  {
                    color: theme.text.primary,
                    backgroundColor: theme.background.input,
                    borderColor: theme.border.default,
                    borderRadius: rounded.sm,
                  },
                ]}
              />
              <Text
                style={[
                  typography["body-sm"],
                  { color: theme.text.muted, textAlign: "right" },
                ]}
              >
                {notes.length}/5000
              </Text>
            </View>

            {/* Save */}
            <TouchableOpacity
              onPress={handleSave}
              disabled={busy}
              activeOpacity={0.8}
              style={[
                styles.saveBtn,
                {
                  backgroundColor: theme.brand.primary,
                  opacity: busy ? 0.5 : 1,
                },
              ]}
            >
              {saving ? (
                <ActivityIndicator color={theme.brand.onPrimary} />
              ) : (
                <Text
                  style={[
                    typography["button"],
                    { color: theme.brand.onPrimary },
                  ]}
                >
                  Save Changes
                </Text>
              )}
            </TouchableOpacity>

            {/* Delete */}
            <TouchableOpacity
              onPress={handleDelete}
              disabled={busy}
              activeOpacity={0.7}
              style={[
                styles.deleteBtn,
                {
                  borderColor: theme.brand.semanticWarning,
                  opacity: busy ? 0.5 : 1,
                },
              ]}
            >
              {deleting ? (
                <ActivityIndicator color={theme.brand.semanticWarning} />
              ) : (
                <Text
                  style={[
                    typography["button"],
                    { color: theme.brand.semanticWarning },
                  ]}
                >
                  Remove from Library
                </Text>
              )}
            </TouchableOpacity>
          </ScrollView>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.6)",
    justifyContent: "flex-end",
  },
  overlayTap: {
    flex: 1,
  },
  sheet: {
    maxHeight: "88%",
  },
  handleWrap: {
    alignItems: "center",
    paddingTop: 8,
    paddingBottom: 4,
  },
  handle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    opacity: 0.5,
  },
  header: {
    flexDirection: "row",
    alignItems: "flex-start",
    paddingBottom: 12,
  },
  statusWrap: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  favRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  pageRow: {
    flexDirection: "row",
    gap: 12,
  },
  input: {
    borderWidth: 1,
    paddingHorizontal: 14,
    paddingVertical: 12,
    minHeight: 48,
  },
  notesInput: {
    borderWidth: 1,
    paddingHorizontal: 14,
    paddingVertical: 12,
    minHeight: 100,
    textAlignVertical: "top",
  },
  progressTrack: {
    height: 6,
    overflow: "hidden",
    marginTop: 8,
  },
  saveBtn: {
    height: 48,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 8,
  },
  deleteBtn: {
    height: 48,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    backgroundColor: "transparent",
  },
});