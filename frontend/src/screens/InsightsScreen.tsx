import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useTheme } from "../theme/ThemeContext";
import { Button } from "../components/Button";
import { api } from "../services/api";

// ─── Types ───────────────────────────────────────────────────────────────────

interface RatingItem {
  content_id: string;
  rating: number;
  book?: {
    title?: string;
  };
  title?: string;
}

interface InsightsData {
  totalRatings: number;
  averageRating: number;
  topRatedTitle: string | null;
  reading: number;
  want_to_read: number;
  finished: number;
  dropped: number;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

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

async function fetchAllRatings(): Promise<RatingItem[]> {
  try {
    const res = await api.get("/users/me/ratings", {
      params: { limit: 100, offset: 0 },
    });
    return res.data?.data?.results ?? [];
  } catch {
    return [];
  }
}

function computeInsights(
  ratings: RatingItem[],
  reading: number,
  want_to_read: number,
  finished: number,
  dropped: number,
): InsightsData {
  const totalRatings = ratings.length;

  const averageRating =
    totalRatings === 0
      ? 0
      : parseFloat(
          (
            ratings.reduce((sum, r) => sum + r.rating, 0) / totalRatings
          ).toFixed(1),
        );

  let topRatedTitle: string | null = null;
  if (ratings.length > 0) {
    const top = ratings.reduce((best, r) =>
      r.rating > best.rating ? r : best,
    );
    topRatedTitle = top.title ?? top.book?.title ?? null;
  }

  return {
    totalRatings,
    averageRating,
    topRatedTitle,
    reading,
    want_to_read,
    finished,
    dropped,
  };
}

// ─── Sub-components ──────────────────────────────────────────────────────────

interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
}

function StatCard({ label, value, sub }: StatCardProps) {
  const { theme, typography, spacing, rounded } = useTheme();
  return (
    <View
      style={[
        statStyles.card,
        {
          backgroundColor: theme.background.card,
          borderRadius: rounded.md,
          padding: spacing.md,
        },
      ]}
    >
      <Text
        style={[
          typography["display-lg"],
          { color: theme.text.primary },
        ]}
        numberOfLines={1}
        adjustsFontSizeToFit
      >
        {value}
      </Text>
      <Text
        style={[
          typography["caption-uppercase"],
          { color: theme.text.muted, marginTop: 4 },
        ]}
        numberOfLines={2}
      >
        {label}
      </Text>
      {sub ? (
        <Text
          style={[
            typography["body-sm"],
            { color: theme.text.secondary, marginTop: 4 },
          ]}
          numberOfLines={2}
        >
          {sub}
        </Text>
      ) : null}
    </View>
  );
}

const statStyles = StyleSheet.create({
  card: {
    flex: 1,
    minHeight: 90,
  },
});

interface StatusBarProps {
  label: string;
  value: number;
  total: number;
  color: string;
}

function StatusBar({ label, value, total, color }: StatusBarProps) {
  const { theme, typography, spacing, rounded } = useTheme();
  const pct = total === 0 ? 0 : Math.round((value / total) * 100);

  return (
    <View style={{ marginBottom: spacing.sm }}>
      <View
        style={{
          flexDirection: "row",
          justifyContent: "space-between",
          marginBottom: 6,
        }}
      >
        <Text
          style={[typography["body-sm"], { color: theme.text.secondary }]}
        >
          {label}
        </Text>
        <Text
          style={[typography["body-sm"], { color: theme.text.muted }]}
        >
          {value} ({pct}%)
        </Text>
      </View>
      <View
        style={[
          barStyles.track,
          {
            backgroundColor: theme.background.elevated,
            borderRadius: rounded.full,
          },
        ]}
      >
        <View
          style={[
            barStyles.fill,
            {
              width: `${pct}%` as any,
              backgroundColor: color,
              borderRadius: rounded.full,
            },
          ]}
        />
      </View>
    </View>
  );
}

const barStyles = StyleSheet.create({
  track: {
    height: 8,
    width: "100%",
  },
  fill: {
    height: 8,
  },
});

// ─── Main Screen ─────────────────────────────────────────────────────────────

export default function InsightsScreen() {
  const { theme, typography, spacing } = useTheme();

  const [data, setData] = useState<InsightsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(false);
    setData(null);

    try {
      const [ratings, reading, want_to_read, finished, dropped] =
        await Promise.all([
          fetchAllRatings(),
          fetchLibraryCount("currently_reading"),
          fetchLibraryCount("want_to_read"),
          fetchLibraryCount("read"),
          fetchLibraryCount("dnf"),
        ]);

      setData(
        computeInsights(ratings, reading, want_to_read, finished, dropped),
      );
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // ── Loading ──────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <View
        style={[styles.center, { backgroundColor: theme.background.primary }]}
      >
        <ActivityIndicator size="large" color={theme.brand.primary} />
      </View>
    );
  }

  // ── Error ────────────────────────────────────────────────────────────────

  if (error || !data) {
    return (
      <View
        style={[
          styles.center,
          { backgroundColor: theme.background.primary, gap: spacing.md },
        ]}
      >
        <Text
          style={[typography["body-md"], { color: theme.text.secondary }]}
        >
          Failed to load insights.
        </Text>
        <Button title="Retry" onPress={loadData} variant="outline" />
      </View>
    );
  }

  const totalLibrary =
    data.reading + data.want_to_read + data.finished + data.dropped;

  // ── Content ──────────────────────────────────────────────────────────────

  return (
    <ScrollView
      style={{ backgroundColor: theme.background.primary }}
      contentContainerStyle={[
        styles.scroll,
        { padding: spacing.lg, gap: spacing.lg },
      ]}
      showsVerticalScrollIndicator={false}
    >
      {/* ── Header ── */}
      <Text
        style={[typography["display-md"], { color: theme.text.primary }]}
      >
        Your Reading Insights
      </Text>

      {/* ── Divider ── */}
      <View
        style={[
          styles.divider,
          { backgroundColor: theme.background.elevated },
        ]}
      />

      {/* ── Top stats row ── */}
      <View style={{ gap: spacing.sm }}>
        <Text
          style={[
            typography["caption-uppercase"],
            { color: theme.text.muted },
          ]}
        >
          Overview
        </Text>
        <View style={[styles.row, { gap: spacing.sm }]}>
          <StatCard label="In Library" value={totalLibrary} />
          <StatCard label="Finished" value={data.finished} />
        </View>
        <View style={[styles.row, { gap: spacing.sm }]}>
         <StatCard label="Ratings" value={data.totalRatings} />
        <StatCard
       label="Avg Rating"
        value={data.averageRating === 0 ? "—" : `${data.averageRating}★`}
          />
        </View>
        {data.topRatedTitle ? (
          <StatCard
            label="Top Rated"
            value="★★★★★"
            sub={data.topRatedTitle}
          />
        ) : null}
      </View>

      {/* ── Divider ── */}
      <View
        style={[
          styles.divider,
          { backgroundColor: theme.background.elevated },
        ]}
      />

      {/* ── Status breakdown ── */}
      <View style={{ gap: spacing.sm }}>
        <Text
          style={[
            typography["caption-uppercase"],
            { color: theme.text.muted },
          ]}
        >
          Library Breakdown
        </Text>

        <StatusBar
          label="Currently Reading"
          value={data.reading}
          total={totalLibrary}
          color={theme.brand.semanticInfo}
        />
        <StatusBar
          label="Want to Read"
          value={data.want_to_read}
          total={totalLibrary}
          color={theme.brand.primary}
        />
        <StatusBar
          label="Finished"
          value={data.finished}
          total={totalLibrary}
          color={theme.brand.semanticSuccess}
        />
        <StatusBar
          label="Dropped"
          value={data.dropped}
          total={totalLibrary}
          color={theme.brand.semanticWarning}
        />
      </View>

      {/* ── Empty state nudge ── */}
      {totalLibrary === 0 && (
        <>
          <View
            style={[
              styles.divider,
              { backgroundColor: theme.background.elevated },
            ]}
          />
          <Text
            style={[
              typography["body-md"],
              { color: theme.text.muted, textAlign: "center" },
            ]}
          >
            Add books to your library to see your reading stats here.
          </Text>
        </>
      )}
    </ScrollView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  scroll: {
    flexGrow: 1,
  },
  row: {
    flexDirection: "row",
  },
  divider: {
    height: 1,
    width: "100%",
  },
});