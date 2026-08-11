import React from "react"
import {
  View,
  Text,
  StyleSheet,
  Image,
  TouchableOpacity,
} from "react-native"
import { useTheme } from "../theme/ThemeContext"
import type { ContentItem } from "../services/collections"

type ContentCardProps = {
  item: ContentItem
  onPress?: (item: ContentItem) => void
}

const CARD_WIDTH = 130
const IMAGE_HEIGHT = 190

const ContentCard: React.FC<ContentCardProps> = ({ item, onPress }) => {
  const { theme, typography, spacing, rounded } = useTheme()

  const handlePress = () => {
    if (onPress) {
      onPress(item)
    }
  }

  return (
    <TouchableOpacity
      activeOpacity={0.8}
      onPress={handlePress}
      style={{ marginRight: spacing.xs }}
    >
      <View
        style={[
          styles.card,
          {
            backgroundColor: theme.background.card,
            borderRadius: rounded.none,
          },
        ]}
      >
        <View style={{ position: "relative" }}>
          {item.cover_url ? (
            <Image
              source={{ uri: item.cover_url }}
              style={{
                width: CARD_WIDTH,
                height: IMAGE_HEIGHT,
                borderRadius: rounded.none,
              }}
              resizeMode="cover"
            />
          ) : (
            <View
              style={{
                width: CARD_WIDTH,
                height: IMAGE_HEIGHT,
                backgroundColor: theme.background.sunken,
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Text
                style={[
                  typography.caption,
                  { color: theme.text.muted },
                ]}
              >
                No Cover
              </Text>
            </View>
          )}

          {item.is_free && (
            <View
              style={{
                position: "absolute",
                top: spacing.xxs,
                left: spacing.xxs,
                backgroundColor: theme.brand.freeReading,
                paddingHorizontal: spacing.xxs,
                paddingVertical: 2,
                borderRadius: rounded.none,
              }}
            >
              <Text
                style={[
                  typography["badge-micro"],
                  { color: "#000" },
                ]}
              >
                FREE
              </Text>
            </View>
          )}
        </View>

        <View style={{ padding: spacing.xxs }}>
          <Text
            numberOfLines={2}
            style={[
              typography["title-sm"],
              { color: theme.text.primary },
            ]}
          >
            {item.title}
          </Text>

          <Text
            numberOfLines={1}
            style={[
              typography.caption,
              { color: theme.text.secondary, marginTop: 2 },
            ]}
          >
            {item.author}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  )
}

const styles = StyleSheet.create({
  card: {
    width: CARD_WIDTH,
  },
})

export default ContentCard