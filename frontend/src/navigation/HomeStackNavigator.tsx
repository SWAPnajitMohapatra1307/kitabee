import React from "react"
import { createNativeStackNavigator } from "@react-navigation/native-stack"
import HomeScreen from "../screens/HomeScreen"
import FullCollectionScreen from "../screens/FullCollectionScreen"

export type HomeStackParamList = {
  HomeMain: undefined
  FullCollection: {
    id: string
    title: string
    items: {
      content_id: string
      title: string
      author: string
      cover_url: string | null
      content_type: string
      is_free: boolean
      free_url: string | null
    }[]
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
    </Stack.Navigator>
  )
}

export default HomeStackNavigator