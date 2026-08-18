import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Linking,
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { useTheme, useThemeStore } from "../theme/ThemeContext";
import { Button } from "../components/Button";
import { api } from "../services/api";
import { authService } from "../services/auth";
import { useUserStore, User } from "../stores/userStore";

type ContentPref = "books" | "comics" | "both";
type ThemeMode = "dark" | "light" | "system";

interface SettingsRowProps {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value?: string;
  onPress: () => void;
  danger?: boolean;
}

function SettingsRow({ icon, label, value, onPress, danger }: SettingsRowProps) {
  const { theme, typography, spacing, rounded } = useTheme();

  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.7}
      style={[
        rowStyles.row,
        {
          backgroundColor: theme.background.card,
          borderRadius: rounded.md,
          paddingVertical: spacing.sm,
          paddingHorizontal: spacing.md,
          minHeight: 56,
        },
      ]}
    >
      <View style={[rowStyles.left, { gap: spacing.sm }]}>
        <Ionicons
          name={icon}
          size={20}
          color={danger ? theme.brand.semanticWarning : theme.text.secondary}
        />
        <Text
          numberOfLines={1}
          style={[
            typography["body-md"],
            {
              flexShrink: 1,
              color: danger ? theme.brand.semanticWarning : theme.text.primary,
            },
          ]}
        >
          {label}
        </Text>
      </View>

      <View style={[rowStyles.right, { gap: spacing.xs }]}>
        {value ? (
          <Text
            style={[
              typography["body-sm"],
              { color: theme.text.muted, maxWidth: 140 },
            ]}
            numberOfLines={1}
          >
            {value}
          </Text>
        ) : null}
        <Ionicons name="chevron-forward" size={18} color={theme.text.muted} />
      </View>
    </TouchableOpacity>
  );
}

const rowStyles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  left: {
    flexDirection: "row",
    alignItems: "center",
    flexShrink: 1,
    flexGrow: 1,
    marginRight: 8,
  },
  right: {
    flexDirection: "row",
    alignItems: "center",
    flexShrink: 0,
  },
});

function SectionHeader({ label }: { label: string }) {
  const { theme, typography } = useTheme();
  return (
    <Text
      style={[
        typography["caption-uppercase"],
        { color: theme.text.muted, marginBottom: 8 },
      ]}
    >
      {label}
    </Text>
  );
}

export default function SettingsScreen() {
  const { theme, typography, spacing } = useTheme();
  const navigation = useNavigation();
  const themeMode = useThemeStore((s) => s.mode);
  const setThemeMode = useThemeStore((s) => s.setMode);

  const [profile, setProfile] = useState<User | null>(null);
  const [contentPref, setContentPref] = useState<ContentPref>("both");
  const [loading, setLoading] = useState(true);

  const [modal, setModal] = useState<
    null | "theme" | "content" | "editProfile" | "password" | "about" | "delete"
  >(null);

  const [name, setName] = useState("");
  const [bio, setBio] = useState("");
  const [currentPass, setCurrentPass] = useState("");
  const [newPass, setNewPass] = useState("");
  const [saving, setSaving] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [meRes, prefsRes] = await Promise.all([
        api.get("/users/me"),
        api.get("/users/me/preferences").catch(() => null),
      ]);

      const user: User = meRes.data?.data;
      setProfile(user);
      setName(user?.name ?? "");
      setBio(user?.bio ?? "");

      const pref = prefsRes?.data?.data?.content_type_preference ?? "both";
      setContentPref(pref);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSetTheme = async (mode: ThemeMode) => {
    setThemeMode(mode);
    setModal(null);
  };

  const handleSetContentPref = async (pref: ContentPref) => {
    setContentPref(pref);
    try {
      await api.put("/users/me/preferences", {
        content_type_preference: pref,
      });
    } catch {
      Alert.alert("Error", "Failed to save preference.");
    }
    setModal(null);
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      const res = await api.patch("/users/me", { name, bio });
      const updated: User = res.data?.data;
      setProfile(updated);
      useUserStore.getState().setUser(updated);
      setModal(null);
    } catch {
      Alert.alert("Error", "Failed to save profile.");
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (newPass.length < 8) {
      Alert.alert("Error", "New password must be at least 8 characters.");
      return;
    }
    setSaving(true);
    try {
      await api.patch("/users/me/password", {
        current_password: currentPass,
        new_password: newPass,
      });
      Alert.alert("Success", "Password changed.");
      setCurrentPass("");
      setNewPass("");
      setModal(null);
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail?.message ?? "Failed to change password.";
      Alert.alert("Error", msg);
    } finally {
      setSaving(false);
    }
  };

  const handleClearCache = () => {
    Alert.alert(
      "Clear Cache",
      "This will clear your local library cache and force a re-sync from the server. Continue?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Clear",
          style: "destructive",
          onPress: async () => {
            try {
              await AsyncStorage.removeItem("kitabee-library");
              Alert.alert("Cache cleared", "Restart the app to re-sync.");
            } catch {
              Alert.alert("Error", "Failed to clear cache.");
            }
          },
        },
      ],
    );
  };

  const handleDeleteAccount = async () => {
    setSaving(true);
    try {
      await api.delete("/users/me");
      await authService.logout();
    } catch {
      Alert.alert("Error", "Failed to delete account.");
      setSaving(false);
    }
  };

  const openMailto = () => {
    Linking.openURL("mailto:support@kitabee.app?subject=Kitabee Support");
  };
  const openPrivacy = () => Linking.openURL("https://kitabee.app/privacy");
  const openTerms = () => Linking.openURL("https://kitabee.app/terms");

  if (loading) {
    return (
      <View
        style={[styles.center, { backgroundColor: theme.background.primary }]}
      >
        <ActivityIndicator size="large" color={theme.brand.primary} />
      </View>
    );
  }

  return (
    <>
      <ScrollView
        style={{ backgroundColor: theme.background.primary }}
        contentContainerStyle={[
          styles.scroll,
          { padding: spacing.lg, gap: spacing.lg },
        ]}
        showsVerticalScrollIndicator={false}
      >
        {/* Header with back button */}
        <View style={styles.topBar}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            activeOpacity={0.7}
            style={styles.backBtn}
            accessibilityLabel="Go back"
          >
            <Ionicons name="chevron-back" size={24} color={theme.text.primary} />
          </TouchableOpacity>
          <Text
            style={[typography["display-md"], { color: theme.text.primary }]}
          >
            Settings
          </Text>
          <View style={{ width: 40 }} />
        </View>

        <View style={{ gap: 8 }}>
          <SectionHeader label="Account" />
          <View style={{ gap: 8 }}>
            <SettingsRow
              icon="person-outline"
              label="Edit Profile"
              value={profile?.name}
              onPress={() => setModal("editProfile")}
            />
            <SettingsRow
              icon="lock-closed-outline"
              label="Change Password"
              onPress={() => setModal("password")}
            />
          </View>
        </View>

        <View style={{ gap: 8 }}>
          <SectionHeader label="Preferences" />
          <View style={{ gap: 8 }}>
            <SettingsRow
              icon="color-palette-outline"
              label="Theme"
              value={
                themeMode === "system"
                  ? "System"
                  : themeMode === "dark"
                  ? "Dark"
                  : "Light"
              }
              onPress={() => setModal("theme")}
            />
            <SettingsRow
              icon="book-outline"
              label="Content"
              value={
                contentPref === "books"
                  ? "Books"
                  : contentPref === "comics"
                  ? "Comics"
                  : "Books + Comics"
              }
              onPress={() => setModal("content")}
            />
          </View>
        </View>

        <View style={{ gap: 8 }}>
          <SectionHeader label="Data" />
          <View style={{ gap: 8 }}>
            <SettingsRow
              icon="refresh-outline"
              label="Clear Local Cache"
              onPress={handleClearCache}
            />
          </View>
        </View>

        <View style={{ gap: 8 }}>
          <SectionHeader label="About" />
          <View style={{ gap: 8 }}>
            <SettingsRow
              icon="mail-outline"
              label="Contact Support"
              onPress={openMailto}
            />
            <SettingsRow
              icon="shield-checkmark-outline"
              label="Privacy Policy"
              onPress={openPrivacy}
            />
            <SettingsRow
              icon="document-text-outline"
              label="Terms of Service"
              onPress={openTerms}
            />
            <SettingsRow
              icon="information-circle-outline"
              label="About Kitabee"
              onPress={() => setModal("about")}
            />
          </View>
        </View>

        <View style={{ gap: 8 }}>
          <SectionHeader label="Danger Zone" />
          <View style={{ gap: 8 }}>
            <SettingsRow
              icon="log-out-outline"
              label="Log Out"
              onPress={() => authService.logout()}
              danger
            />
            <SettingsRow
              icon="trash-outline"
              label="Delete Account"
              onPress={() => setModal("delete")}
              danger
            />
          </View>
        </View>

        <View style={{ height: spacing.lg }} />
      </ScrollView>

      <SettingsModal
        visible={modal === "theme"}
        title="Choose Theme"
        onClose={() => setModal(null)}
      >
        <ChoiceRow
          label="System Default"
          selected={themeMode === "system"}
          onPress={() => handleSetTheme("system")}
        />
        <ChoiceRow
          label="Dark"
          selected={themeMode === "dark"}
          onPress={() => handleSetTheme("dark")}
        />
        <ChoiceRow
          label="Light"
          selected={themeMode === "light"}
          onPress={() => handleSetTheme("light")}
        />
      </SettingsModal>

      <SettingsModal
        visible={modal === "content"}
        title="Content Preference"
        onClose={() => setModal(null)}
      >
        <ChoiceRow
          label="Books Only"
          selected={contentPref === "books"}
          onPress={() => handleSetContentPref("books")}
        />
        <ChoiceRow
          label="Comics Only"
          selected={contentPref === "comics"}
          onPress={() => handleSetContentPref("comics")}
        />
        <ChoiceRow
          label="Books + Comics"
          selected={contentPref === "both"}
          onPress={() => handleSetContentPref("both")}
        />
      </SettingsModal>

      <SettingsModal
        visible={modal === "editProfile"}
        title="Edit Profile"
        onClose={() => setModal(null)}
      >
        <FormLabel label="Name" />
        <FormInput value={name} onChangeText={setName} />
        <View style={{ height: spacing.sm }} />
        <FormLabel label="Bio" />
        <FormInput
          value={bio}
          onChangeText={setBio}
          multiline
          numberOfLines={4}
        />
        <View style={{ height: spacing.md }} />
        <Button
          title={saving ? "Saving..." : "Save"}
          onPress={handleSaveProfile}
          disabled={saving}
        />
      </SettingsModal>

      <SettingsModal
        visible={modal === "password"}
        title="Change Password"
        onClose={() => setModal(null)}
      >
        <FormLabel label="Current Password" />
        <FormInput
          value={currentPass}
          onChangeText={setCurrentPass}
          secureTextEntry
        />
        <View style={{ height: spacing.sm }} />
        <FormLabel label="New Password (min 8 characters)" />
        <FormInput
          value={newPass}
          onChangeText={setNewPass}
          secureTextEntry
        />
        <View style={{ height: spacing.md }} />
        <Button
          title={saving ? "Changing..." : "Change Password"}
          onPress={handleChangePassword}
          disabled={saving}
        />
      </SettingsModal>

      <SettingsModal
        visible={modal === "about"}
        title="About Kitabee"
        onClose={() => setModal(null)}
      >
        <AboutBody />
      </SettingsModal>

      <SettingsModal
        visible={modal === "delete"}
        title="Delete Account?"
        onClose={() => setModal(null)}
      >
        <Text
          style={[
            typography["body-md"],
            { color: theme.text.secondary, marginBottom: spacing.md },
          ]}
        >
          This will permanently delete your account, ratings, library, and
          preferences. This action cannot be undone.
        </Text>
        <Button
          title={saving ? "Deleting..." : "Yes, Delete My Account"}
          onPress={handleDeleteAccount}
          disabled={saving}
          variant="outline"
        />
      </SettingsModal>
    </>
  );
}

interface SettingsModalProps {
  visible: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}

function SettingsModal({
  visible,
  title,
  onClose,
  children,
}: SettingsModalProps) {
  const { theme, typography, spacing, rounded } = useTheme();

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={modalStyles.overlay}>
        <View
          style={[
            modalStyles.sheet,
            {
              backgroundColor: theme.background.card,
              borderTopLeftRadius: rounded.lg,
              borderTopRightRadius: rounded.lg,
              padding: spacing.lg,
            },
          ]}
        >
          <View
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: spacing.md,
            }}
          >
            <Text
              style={[typography["title-md"], { color: theme.text.primary }]}
            >
              {title}
            </Text>
            <TouchableOpacity onPress={onClose} activeOpacity={0.7}>
              <Ionicons name="close" size={24} color={theme.text.secondary} />
            </TouchableOpacity>
          </View>
          {children}
        </View>
      </View>
    </Modal>
  );
}

const modalStyles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "flex-end",
  },
  sheet: {
    minHeight: 200,
    maxHeight: "80%",
  },
});

function ChoiceRow({
  label,
  selected,
  onPress,
}: {
  label: string;
  selected: boolean;
  onPress: () => void;
}) {
  const { theme, typography, spacing } = useTheme();
  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.7}
      style={{
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "space-between",
        paddingVertical: spacing.sm,
      }}
    >
      <Text style={[typography["body-md"], { color: theme.text.primary }]}>
        {label}
      </Text>
      {selected ? (
        <Ionicons name="checkmark" size={22} color={theme.brand.primary} />
      ) : null}
    </TouchableOpacity>
  );
}

function FormLabel({ label }: { label: string }) {
  const { theme, typography } = useTheme();
  return (
    <Text
      style={[
        typography["caption-uppercase"],
        { color: theme.text.muted, marginBottom: 6 },
      ]}
    >
      {label}
    </Text>
  );
}

function FormInput(props: React.ComponentProps<typeof TextInput>) {
  const { theme, typography, rounded } = useTheme();
  return (
    <TextInput
      {...props}
      placeholderTextColor={theme.text.muted}
      style={[
        typography["body-md"],
        {
          color: theme.text.primary,
          backgroundColor: theme.background.input,
          borderColor: theme.border.default,
          borderWidth: 1,
          borderRadius: rounded.sm,
          padding: 12,
          minHeight: 48,
        },
        props.multiline
          ? { minHeight: 100, textAlignVertical: "top" }
          : null,
      ]}
    />
  );
}

function AboutBody() {
  const { theme, typography, spacing } = useTheme();
  return (
    <View style={{ gap: spacing.sm }}>
      <Text style={[typography["display-md"], { color: theme.brand.primary }]}>
        Kitabee 🐝
      </Text>
      <Text style={[typography["body-md"], { color: theme.text.primary }]}>
        Version 1.0.0
      </Text>
      <Text style={[typography["body-sm"], { color: theme.text.secondary }]}>
        Kitabee is your personal library and discovery engine for books and
        comics. Powered by AI-driven recommendations, mood-based collections,
        and free public-domain reading.
      </Text>
      <Text
        style={[
          typography["body-sm"],
          { color: theme.text.muted, marginTop: spacing.sm },
        ]}
      >
        Built with FastAPI + React Native + Expo.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  scroll: {
    flexGrow: 1,
  },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  backBtn: {
    width: 40,
    height: 40,
    alignItems: "center",
    justifyContent: "center",
  },
});