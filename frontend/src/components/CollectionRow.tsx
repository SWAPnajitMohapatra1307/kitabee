import React from "react"
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
} from "react-native"
import { useTheme } from "../theme/ThemeContext"
import ContentCard from "./ContentCard"
import type { Collection, ContentItem } from "../services/collections"

type CollectionRowProps = {
  collection: Collection
  onItemPress?: (item: ContentItem) => void
  onSeeAllPress?: (collection: Collection) => void
}

const CollectionRow: React.FC<CollectionRowProps> = ({
  collection,
  onItemPress,
  onSeeAllPress,
}) => {
  const { theme, typography, spacing } = useTheme()

  if (!collection.items || collection.items.length === 0) {
    return null
  }

  return (
    <View style={{ marginBottom: spacing.sm }}>
      <View
        style={{
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center",
          paddingHorizontal: spacing.xs,
          marginBottom: spacing.xxs,
        }}
      >
        <Text
          style={[
            typography["row-title"],
            { color: theme.text.primary, flex: 1 },
          ]}
          numberOfLines={1}
        >
          {collection.title}
        </Text>

        {onSeeAllPress && (
          <TouchableOpacity
            onPress={() => onSeeAllPress(collection)}
            activeOpacity={0.7}
          >
            <Text
              style={[
                typography["caption-uppercase"],
                { color: theme.brand.primary },
              ]}
            >
              See All
            </Text>
          </TouchableOpacity>
        )}
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: spacing.xs,
        }}
      >
        {collection.items.map((item) => (
          <ContentCard
            key={item.content_id}
            item={item}
            onPress={onItemPress}
          />
        ))}
      </ScrollView>
    </View>
  )
}

export default CollectionRow