import React from "react"
import { createNativeStackNavigator } from "@react-navigation/native-stack"
import HomeScreen from "../screens/HomeScreen"
import FullCollectionScreen from "../screens/FullCollectionScreen"
import BookDetailScreen from "../screens/BookDetailScreen"
import type { Collection } from "../services/collections"

export type HomeStackParamList = {
  HomeMain: undefined
  BookDetail: { content_id: string }
  FullCollection: {
    id: string
    title: string
    items: Collection["items"]
  }
}

const Stack = createNativeStackNavigator<HomeStackParamList>()

const HomeStackNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="HomeMain" component={HomeScreen} />
      <Stack.Screen name="FullCollection" component={FullCollectionScreen} />
      <Stack.Screen
        name="BookDetail"
        component={BookDetailScreen}
        getId={({ params }) => params.content_id}
      />
    </Stack.Navigator>
  )
}

export default HomeStackNavigator