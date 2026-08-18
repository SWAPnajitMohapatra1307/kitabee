import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import { Ionicons } from "@expo/vector-icons";
import { useTheme } from "../theme/ThemeContext";
import { Button } from "../components/Button";
import { api } from "../services/api";
import { useUserStore, User } from "../stores/userStore";

interface LibraryCounts {
  reading: number;
  want_to_read: number;
  finished: number;
  dropped: number;
}

function formatJoinDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-IN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

async function fetchLibraryCount(status: string): Promise<number> {
  try {
    const res = await api.get("/library", {
      params: { status, limit: 1, offset: 0 },
    });
    return res.data?.data?.total ?? 0;
  } catch {
    return 0;
  }
}

interface StatTileProps {
  label: string;
  value: number;
}

function StatTile({ label, value }: StatTileProps) {
  const { theme, typography, spacing, rounded } = useTheme();
  return (
    <View
      style={[
        statTileStyles.tile,
        {
          backgroundColor: theme.background.card,
          borderRadius: rounded.md,
          paddingVertical: spacing.md,
          paddingHorizontal: spacing.sm,
        },
      ]}
    >
      <Text
        style={{
          color: theme.text.primary,
          fontSize: 36,
          fontWeight: "700",
          lineHeight: 42,
          textAlign: "center",
        }}
        numberOfLines={1}
      >
        {value}
      </Text>
      <Text
        style={[
          typography["caption-uppercase"],
          {
            color: theme.text.muted,
            marginTop: 8,
            fontSize: 11,
            textAlign: "center",
          },
        ]}
        numberOfLines={1}
      >
        {label}
      </Text>
    </View>
  );
}

const statTileStyles = StyleSheet.create({
  tile: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    minHeight: 96,
  },
});

export default function ProfileScreen() {
  const { theme, typography, spacing, rounded } = useTheme();
  const navigation = useNavigation<any>();

  const [profile, setProfile] = useState<User | null>(null);
  const [counts, setCounts] = useState<LibraryCounts>({
    reading: 0,
    want_to_read: 0,
    finished: 0,
    dropped: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(false);

    try {
      const [meRes, reading, want_to_read, finished, dropped] =
        await Promise.all([
          api.get("/users/me"),
          fetchLibraryCount("currently_reading"),
          fetchLibraryCount("want_to_read"),
          fetchLibraryCount("read"),
          fetchLibraryCount("dnf"),
        ]);

      const user: User = meRes.data?.data;
      if (!user) throw new Error("empty profile");

      useUserStore.getState().setUser(user);
      setProfile(user);
      setCounts({ reading, want_to_read, finished, dropped });
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <View
        style={[styles.center, { backgroundColor: theme.background.primary }]}
      >
        <ActivityIndicator size="large" color={theme.brand.primary} />
      </View>
    );
  }

  if (error || !profile) {
    return (
      <View
        style={[
          styles.center,
          { backgroundColor: theme.background.primary, gap: spacing.md },
        ]}
      >
        <Text style={[typography["body-md"], { color: theme.text.secondary }]}>
          Failed to load profile.
        </Text>
        <Button title="Retry" onPress={loadData} variant="outline" />
      </View>
    );
  }

  return (
    <ScrollView
      style={{ backgroundColor: theme.background.primary }}
      contentContainerStyle={[
        styles.scroll,
        { padding: spacing.lg, gap: spacing.lg },
      ]}
      showsVerticalScrollIndicator={false}
    >
      {/* Gear icon */}
      <View style={styles.topBar}>
        <View style={{ flex: 1 }} />
        <TouchableOpacity
          onPress={() => navigation.navigate("Settings")}
          activeOpacity={0.7}
          style={[
            styles.gearBtn,
            { backgroundColor: theme.background.elevated },
          ]}
        >
          <Ionicons name="settings-outline" size={20} color={theme.text.primary} />
        </TouchableOpacity>
      </View>

      {/* Avatar + name */}
      <View style={[styles.header, { gap: spacing.sm }]}>
        <View
          style={[
            styles.avatar,
            {
              backgroundColor: theme.background.elevated,
              borderRadius: rounded.full,
              borderWidth: 2,
              borderColor: theme.brand.primary,
            },
          ]}
        >
          <Text
            style={[typography["display-lg"], { color: theme.brand.primary }]}
          >
            {profile.name.charAt(0).toUpperCase()}
          </Text>
        </View>

        <Text style={[typography["display-md"], { color: theme.text.primary }]}>
          {profile.name}
        </Text>

        <Text
          style={[typography["body-sm"], { color: theme.text.secondary }]}
          numberOfLines={1}
        >
          {profile.email}
        </Text>

        <Text
          style={[typography["caption-uppercase"], { color: theme.text.muted }]}
        >
          Joined {formatJoinDate(profile.created_at)}
        </Text>
      </View>

      {/* Divider */}
      <View
        style={[
          styles.divider,
          { backgroundColor: theme.background.elevated },
        ]}
      />

      {/* Library stats — 2x2 grid */}
      <View style={{ gap: spacing.sm }}>
        <Text
          style={[
            typography["caption-uppercase"],
            { color: theme.text.muted },
          ]}
        >
          My Library
        </Text>

        <View style={[styles.statsRow, { gap: spacing.sm }]}>
          <StatTile label="Reading" value={counts.reading} />
          <StatTile label="Want to Read" value={counts.want_to_read} />
        </View>
        <View style={[styles.statsRow, { gap: spacing.sm }]}>
          <StatTile label="Finished" value={counts.finished} />
          <StatTile label="Dropped" value={counts.dropped} />
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  scroll: { flexGrow: 1 },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-end",
  },
  gearBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
  },
  header: { alignItems: "center" },
  avatar: {
    width: 80,
    height: 80,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 4,
  },
  divider: { height: 1, width: "100%" },
  statsRow: { flexDirection: "row" },
});