import React, { useState } from "react"
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
} from "react-native"
import { useTheme } from "../theme/ThemeContext"
import type { ContentItem } from "../services/collections"

type ContentCardProps = {
  item: ContentItem
  onPress?: (item: ContentItem) => void
}

const CARD_WIDTH = 130
const COVER_HEIGHT = 180

const ContentCard: React.FC<ContentCardProps> = ({ item, onPress }) => {
  const { theme, typography, spacing, rounded } = useTheme()
  const [imageError, setImageError] = useState(false)

  const hasCover = !!item.cover_url && !imageError
  const authorName = item.author || (item as any).authors?.[0] || ""

  return (
    <TouchableOpacity
      activeOpacity={0.8}
      onPress={() => onPress?.(item)}
      style={[
        styles.card,
        {
          width: CARD_WIDTH,
          marginRight: spacing.xs,
        },
      ]}
    >
      {/* Cover Image OR Styled Title-Card Fallback */}
      <View
        style={[
          styles.coverContainer,
          {
            height: COVER_HEIGHT,
            borderRadius: rounded.sm,
            backgroundColor: theme.background.elevated,
          },
        ]}
      >
        {hasCover ? (
          <Image
            source={{ uri: item.cover_url! }}
            style={[
              styles.coverImage,
              { borderRadius: rounded.sm },
            ]}
            resizeMode="cover"
            onError={() => setImageError(true)}
          />
        ) : (
          /* Styled Fallback Cover for Missing/Failed Images */
          <View
            style={[
              styles.fallbackCover,
              {
                borderRadius: rounded.sm,
                backgroundColor: theme.brand.primary,
                padding: spacing.xs,
              },
            ]}
          >
            <Text
              style={[
                typography["title-sm"],
                {
                  color: theme.brand.onPrimary,
                  textAlign: "center",
                },
              ]}
              numberOfLines={4}
            >
              {item.title}
            </Text>
            {authorName ? (
              <Text
                style={[
                  typography["caption-uppercase"],
                  {
                    color: theme.brand.onPrimary,
                    textAlign: "center",
                    marginTop: spacing.xxs,
                    opacity: 0.85,
                    fontSize: 10,
                  },
                ]}
                numberOfLines={1}
              >
                {authorName}
              </Text>
            ) : null}
          </View>
        )}

        {/* FREE Tag Badge */}
        {item.is_free && (
          <View
            style={[
              styles.freeBadge,
              {
                backgroundColor: "#F59E0B", // Vibrant Gold/Amber
                borderBottomRightRadius: rounded.xs,
                borderTopLeftRadius: rounded.sm,
              },
            ]}
          >
            <Text style={styles.freeBadgeText}>FREE</Text>
          </View>
        )}
      </View>

      {/* Book Title & Author Below Cover */}
      <View style={{ marginTop: spacing.xxs }}>
        <Text
          style={[
            typography["title-sm"],
            { color: theme.text.primary },
          ]}
          numberOfLines={2}
        >
          {item.title}
        </Text>

        <Text
          style={[
            typography["caption-uppercase"],
            { color: theme.text.secondary, marginTop: 2 },
          ]}
          numberOfLines={1}
        >
          {authorName || "Unknown Author"}
        </Text>
      </View>
    </TouchableOpacity>
  )
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "column",
  },
  coverContainer: {
    width: "100%",
    position: "relative",
    overflow: "hidden",
  },
  coverImage: {
    width: "100%",
    height: "100%",
  },
  fallbackCover: {
    width: "100%",
    height: "100%",
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 3,
  },
  freeBadge: {
    position: "absolute",
    top: 0,
    left: 0,
    paddingHorizontal: 6,
    paddingVertical: 2,
    zIndex: 2,
  },
  freeBadgeText: {
    color: "#FFFFFF",
    fontSize: 9,
    fontWeight: "800",
    letterSpacing: 0.5,
  },
})

export default ContentCard