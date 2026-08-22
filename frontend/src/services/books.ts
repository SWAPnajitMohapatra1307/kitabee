import { api } from "./api";
import type { ContentSource, ContentType } from "./collections";

export type Book = {
  content_id: string;
  external_id?: string;
  external_source?: ContentSource;
  title: string;
  author: string | null;
  authors?: string[];
  description: string | null;
  cover_url: string | null;
  cover_url_large?: string | null;
  content_type?: ContentType;
  is_free?: boolean;
  free_url?: string | null;
  genres?: string[];
  language?: string | null;
  publisher?: string | null;
  published_date?: string | null;
  page_count?: number | null;
  isbn_10?: string | null;
  isbn_13?: string | null;
  average_rating?: number | null;
  rating_count?: number;
  series_id?: string | null;
  series_order?: number | null;
  source?: ContentSource;
};

export type SimilarBooksResponse = {
  items?: Book[];
  results?: Book[];
  total?: number;
  total_count?: number;
};

export type SearchResponse = {
  items?: Book[];
  results?: Book[];
  total?: number;
  total_count?: number;
};

export type SeriesItem = {
  content_id: string;
  title: string | null;
  position: number | null;
  label:
    | "You Are Here"
    | "Read This First"
    | "Read This Next"
    | "Coming Up"
    | "Also In This Series";
};

export type SeriesResponse = {
  series_name: string;
  total: number;
  current_position: number | null;
  items: SeriesItem[];
} | null;

export async function fetchBookById(contentId: string): Promise<Book> {
  const response = await api.get(`/books/${encodeURIComponent(contentId)}`);
  return response.data.data as Book;
}

export async function fetchSimilarBooks(
  contentId: string,
  limit: number = 10
): Promise<Book[]> {
  const response = await api.get(
    `/books/${encodeURIComponent(contentId)}/similar`,
    { params: { limit } }
  );
  const payload = response.data?.data as SimilarBooksResponse;
  return payload?.items ?? payload?.results ?? [];
}

export async function searchBooks(
  query: string,
  limit: number = 20
): Promise<Book[]> {
  const response = await api.get("/books/search", {
    params: { q: query, limit },
  });
  const payload = response.data?.data as SearchResponse;
  return payload?.items ?? payload?.results ?? [];
}

export async function fetchSeriesData(
  contentId: string
): Promise<SeriesResponse> {
  const response = await api.get(
    `/books/${encodeURIComponent(contentId)}/series`
  );
  return response.data?.data as SeriesResponse;
}