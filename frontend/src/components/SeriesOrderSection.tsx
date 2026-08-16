import React from "react"
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
} from "react-native"
import { useTheme } from "../theme/ThemeContext"
import type { SeriesItem, SeriesResponse } from "../services/books"

type Props = {
  series: SeriesResponse
  onItemPress: (content_id: string) => void
  currentContentId: string
}

const LABEL_ORDER: Record<SeriesItem["label"], number> = {
  "Read This First": 0,
  "You Are Here": 1,
  "Read This Next": 2,
  "Coming Up": 3,
  "Also In This Series": 4,
}

function labelColor(
  label: SeriesItem["label"],
  theme: ReturnType<typeof useTheme>["theme"]
): string {
  switch (label) {
    case "You Are Here":
      return theme.brand.primary
    case "Read This First":
      return theme.brand.semanticInfo
    case "Read This Next":
      return theme.brand.semanticSuccess
    case "Coming Up":
      return theme.text.muted
    case "Also In This Series":
      return theme.text.muted
  }
}

const SeriesOrderSection: React.FC<Props> = ({
  series,
  onItemPress,
  currentContentId,
}) => {
  const { theme, typography, spacing, rounded } = useTheme()

  if (!series || !series.items || series.items.length === 0) {
    return null
  }

  const sorted = [...series.items].sort((a, b) => {
    const posA = a.position ?? 9999
    const posB = b.position ?? 9999
    if (posA !== posB) return posA - posB
    return LABEL_ORDER[a.label] - LABEL_ORDER[b.label]
  })

  return (
    <View style={{ marginTop: spacing.lg }}>
      <View
        style={{
          paddingHorizontal: spacing.md,
          marginBottom: spacing.sm,
        }}
      >
        <Text
          style={[typography["title-md"], { color: theme.text.primary }]}
        >
          {series.series_name}
        </Text>
        <Text
          style={[
            typography["body-sm"],
            { color: theme.text.muted, marginTop: 2 },
          ]}
        >
          {series.total} {series.total === 1 ? "book" : "books"} in series
          {series.current_position != null
            ? ` · You are at #${series.current_position}`
            : ""}
        </Text>
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: spacing.md,
          gap: spacing.sm,
        }}
      >
        {sorted.map((item) => {
          const isCurrentBook = item.content_id === currentContentId
          const color = labelColor(item.label, theme)

          return (
            <TouchableOpacity
              key={item.content_id}
              onPress={() => {
                if (!isCurrentBook) {
                  onItemPress(item.content_id)
                }
              }}
              activeOpacity={isCurrentBook ? 1 : 0.7}
              style={{
                width: 120,
                backgroundColor: isCurrentBook
                  ? theme.background.elevated
                  : theme.background.card,
                borderRadius: rounded.md,
                padding: spacing.sm,
                borderWidth: isCurrentBook ? 2 : 1,
                borderColor: isCurrentBook
                  ? theme.brand.primary
                  : theme.background.elevated,
              }}
            >
              <View
                style={{
                  backgroundColor: theme.background.sunken,
                  borderRadius: rounded.sm,
                  alignItems: "center",
                  justifyContent: "center",
                  height: 100,
                  marginBottom: spacing.xs,
                }}
              >
                {item.position != null ? (
                  <Text
                    style={[
                      typography["number-display"],
                      { color: theme.text.muted, fontSize: 28 },
                    ]}
                  >
                    #{item.position}
                  </Text>
                ) : (
                  <Text
                    style={[
                      typography["body-sm"],
                      { color: theme.text.disabled },
                    ]}
                  >
                    ?
                  </Text>
                )}
              </View>

              <Text
                style={[
                  typography["body-sm"],
                  {
                    color: theme.text.primary,
                    marginBottom: 4,
                  },
                ]}
                numberOfLines={2}
              >
                {item.title ?? "Untitled"}
              </Text>

              <Text
                style={[
                  typography["badge-micro"],
                  {
                    color,
                  },
                ]}
                numberOfLines={1}
              >
                {item.label}
              </Text>
            </TouchableOpacity>
          )
        })}
      </ScrollView>
    </View>
  )
}

export default SeriesOrderSection