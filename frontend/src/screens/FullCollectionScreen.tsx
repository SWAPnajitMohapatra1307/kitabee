import React from "react"
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  useWindowDimensions,
} from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import { RouteProp, useNavigation, useRoute } from "@react-navigation/native"
import { NativeStackNavigationProp } from "@react-navigation/native-stack"
import { useTheme } from "../theme/ThemeContext"
import ContentCard from "../components/ContentCard"
import { HomeStackParamList } from "../navigation/HomeStackNavigator"

type FullCollectionRouteProp = RouteProp<HomeStackParamList, "FullCollection">
type FullCollectionNavProp = NativeStackNavigationProp<
  HomeStackParamList,
  "FullCollection"
>

function getColumnCount(width: number): number {
  if (width >= 1400) return 6
  if (width >= 1024) return 5
  if (width >= 768) return 4
  if (width >= 480) return 3
  return 2
}

const FullCollectionScreen: React.FC = () => {
  const { theme, typography, spacing } = useTheme()
  const route = useRoute<FullCollectionRouteProp>()
  const navigation = useNavigation<FullCollectionNavProp>()
  const { width } = useWindowDimensions()

  const { title, items } = route.params
  const numColumns = getColumnCount(width)

  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: theme.background.primary }}
    >
      <View
        style={{
          flexDirection: "row",
          alignItems: "center",
          paddingHorizontal: spacing.xs,
          paddingVertical: spacing.xxs,
          borderBottomWidth: 1,
          borderBottomColor: theme.border.default,
        }}
      >
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          activeOpacity={0.7}
          style={{ paddingRight: spacing.xs }}
        >
          <Text
            style={[typography["title-md"], { color: theme.text.primary }]}
          >
            ‹
          </Text>
        </TouchableOpacity>
        <Text
          numberOfLines={1}
          style={[
            typography["title-md"],
            { color: theme.text.primary, flex: 1 },
          ]}
        >
          {title}
        </Text>
      </View>

      <FlatList
        key={`cols-${numColumns}`}
        data={items}
        keyExtractor={(item) => item.content_id}
        numColumns={numColumns}
        contentContainerStyle={{ padding: spacing.xs }}
        columnWrapperStyle={
          numColumns > 1
            ? { gap: spacing.xs }
            : undefined
        }
        renderItem={({ item }) => (
          <View style={{ flex: 1 / numColumns, marginBottom: spacing.xs }}>
            <ContentCard
              item={item}
              onPress={(i) =>
                navigation.navigate("BookDetail", { content_id: i.content_id })
              }
            />
          </View>
        )}
        ListEmptyComponent={
          <View
            style={{
              alignItems: "center",
              justifyContent: "center",
              padding: spacing.lg,
            }}
          >
            <Text
              style={[typography["body-md"], { color: theme.text.secondary }]}
            >
              No items in this collection.
            </Text>
          </View>
        }
      />
    </SafeAreaView>
  )
}

export default FullCollectionScreen