import React, { memo, useCallback } from "react"
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
} from "react-native"
import { useTheme } from "../theme/ThemeContext"
import ContentCard from "./ContentCard"
import type { Collection, ContentItem } from "../services/collections"

type CollectionRowProps = {
  collection: Collection
  onItemPress?: (item: ContentItem) => void
  onSeeAllPress?: (collection: Collection) => void
}

const CARD_WIDTH = 130

const CollectionRow: React.FC<CollectionRowProps> = ({
  collection,
  onItemPress,
  onSeeAllPress,
}) => {
  const { theme, typography, spacing } = useTheme()

  const renderCard = useCallback(
    ({ item }: { item: ContentItem }) => (
      <ContentCard item={item} onPress={onItemPress} />
    ),
    [onItemPress]
  )

  const getItemLayout = useCallback(
    (_: any, index: number) => ({
      length: CARD_WIDTH + spacing.xs, // Card width (130) + marginRight spacing
      offset: (CARD_WIDTH + spacing.xs) * index,
      index,
    }),
    [spacing.xs]
  )

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

      <FlatList
        horizontal
        data={collection.items}
        keyExtractor={(item) => item.content_id}
        renderItem={renderCard}
        initialNumToRender={5}
        maxToRenderPerBatch={3}
        windowSize={3}
        showsHorizontalScrollIndicator={false}
        removeClippedSubviews={true}
        getItemLayout={getItemLayout}
        contentContainerStyle={{
          paddingHorizontal: spacing.xs,
        }}
      />
    </View>
  )
}

export default memo(CollectionRow)