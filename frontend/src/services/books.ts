import { api } from "./api";
import type { ContentSource, ContentType } from "./collections";

export type Book = {
  content_id: string;
  external_id: string;
  external_source: ContentSource;
  title: string;
  author: string | null;
  authors: string[];
  description: string | null;
  cover_url: string | null;
  cover_url_large: string | null;
  content_type: ContentType;
  is_free: boolean;
  free_url: string | null;
  genres: string[];
  language: string | null;
  publisher: string | null;
  published_date: string | null;
  page_count: number | null;
  isbn_10: string | null;
  isbn_13: string | null;
  average_rating: number | null;
  rating_count: number;
  series_id: string | null;
  series_order: number | null;
  source: ContentSource;
};

export type SimilarBooksResponse = {
  total_count: number;
  limit: number;
  offset: number;
  results: Book[];
};

export type SearchResponse = {
  total_count: number;
  limit: number;
  offset: number;
  results: Book[];
};

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
  const payload = response.data.data as SimilarBooksResponse;
  return payload?.results ?? [];
}

export async function searchBooks(
  query: string,
  limit: number = 20
): Promise<Book[]> {
  const response = await api.get("/books/search", {
    params: { q: query, limit },
  });
  const payload = response.data.data as SearchResponse;
  return payload?.results ?? [];
}