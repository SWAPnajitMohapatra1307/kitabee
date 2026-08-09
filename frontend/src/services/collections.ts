import {api} from "./api"

export type ContentItem = {
  content_id: string
  title: string
  author: string
  cover_url: string | null
  content_type: string
  is_free: boolean
  free_url: string | null
}

export type Collection = {
  id: string
  title: string
  items: ContentItem[]
}

export type CollectionsResponse = {
  rows: Collection[]
}

export async function fetchCollections(): Promise<Collection[]> {
  const response = await api.get("/collections")
  console.log("Collections raw response:", JSON.stringify(response.data, null, 2))
  const payload = response.data.data as CollectionsResponse
  return payload?.rows ?? []
}