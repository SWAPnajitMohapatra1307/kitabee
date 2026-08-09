import React, { useEffect, useState } from "react"
import {
  ScrollView,
  View,
  Text,
  ActivityIndicator,
  RefreshControl,
} from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import { useNavigation } from "@react-navigation/native"
import { NativeStackNavigationProp } from "@react-navigation/native-stack"
import { useTheme } from "../theme/ThemeContext"
import CollectionRow from "../components/CollectionRow"
import {
  fetchCollections,
  Collection,
  ContentItem,
} from "../services/collections"
import { HomeStackParamList } from "../navigation/HomeStackNavigator"

type HomeNavProp = NativeStackNavigationProp<HomeStackParamList, "HomeMain">

const HomeScreen: React.FC = () => {
  const { theme, typography, spacing } = useTheme()
  const navigation = useNavigation<HomeNavProp>()

  const [collections, setCollections] = useState<Collection[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [refreshing, setRefreshing] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const loadCollections = async () => {
    try {
      setError(null)
      const rows = await fetchCollections()
      setCollections(rows)
    } catch (err: any) {
      const msg =
        err?.response?.data?.error?.message ||
        err?.message ||
        "Failed to load collections"
      setError(msg)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadCollections()
  }, [])

  const handleRefresh = () => {
    setRefreshing(true)
    loadCollections()
  }

  const handleItemPress = (item: ContentItem) => {
    console.log("Tap item:", item.title)
  }

  const handleSeeAllPress = (collection: Collection) => {
    navigation.navigate("FullCollection", {
      id: collection.id,
      title: collection.title,
      items: collection.items,
    })
  }

  if (loading) {
    return (
      <SafeAreaView
        style={{
          flex: 1,
          backgroundColor: theme.background.primary,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ActivityIndicator size="large" color={theme.brand.primary} />
      </SafeAreaView>
    )
  }

  if (error) {
    return (
      <SafeAreaView
        style={{
          flex: 1,
          backgroundColor: theme.background.primary,
          alignItems: "center",
          justifyContent: "center",
          padding: spacing.sm,
        }}
      >
        <Text
          style={[
            typography["body-md"],
            { color: theme.text.primary, textAlign: "center" },
          ]}
        >
          {error}
        </Text>
      </SafeAreaView>
    )
  }

  if (collections.length === 0) {
    return (
      <SafeAreaView
        style={{
          flex: 1,
          backgroundColor: theme.background.primary,
          alignItems: "center",
          justifyContent: "center",
          padding: spacing.sm,
        }}
      >
        <Text
          style={[
            typography["body-md"],
            { color: theme.text.secondary, textAlign: "center" },
          ]}
        >
          No collections yet.
        </Text>
      </SafeAreaView>
    )
  }

  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: theme.background.primary }}
    >
      <ScrollView
        contentContainerStyle={{ paddingVertical: spacing.sm }}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={theme.brand.primary}
          />
        }
      >
        {collections.map((col) => (
          <CollectionRow
            key={col.id}
            collection={col}
            onItemPress={handleItemPress}
            onSeeAllPress={handleSeeAllPress}
          />
        ))}
      </ScrollView>
    </SafeAreaView>
  )
}

export default HomeScreen