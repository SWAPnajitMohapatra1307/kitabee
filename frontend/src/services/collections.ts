import { api } from "./api";

export type ContentSource = "google_books" | "comic_vine" | "internet_archive";
export type ContentType = "book" | "comic";

export type ContentItem = {
  content_id: string;
  title: string;
  author: string;
  cover_url: string | null;
  content_type: ContentType;
  is_free: boolean;
  free_url: string | null;
  source: ContentSource;
  description: string | null;
  genres: string[];
};

export type Collection = {
  id: string;
  title: string;
  mood: string;
  items: ContentItem[];
  item_count: number;
};

export type CollectionsResponse = {
  rows: Collection[];
  total: number;
  personalized: boolean;
};

export async function fetchCollections(): Promise<Collection[]> {
  const response = await api.get("/collections");
  const payload = response.data.data as CollectionsResponse;
  return payload?.rows ?? [];
}