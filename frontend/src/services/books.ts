import {api} from './api';

export interface Book {
  id: string;
  title: string;
  author: string;
  description: string | null;
  cover_url: string | null;
  content_type: 'book' | 'comic';
  is_free: boolean;
  free_url: string | null;
  genres: string[];
  average_rating: number | null;
  rating_count: number;
  isbn: string | null;
  series_id: string | null;
  series_order: number | null;
}

export interface SimilarBooksResponse {
  items: Book[];
  total: number;
}

export async function fetchBookById(bookId: string): Promise<Book> {
  const response = await api.get(`/books/${bookId}`);
  return response.data.data;
}

export async function fetchSimilarBooks(bookId: string): Promise<Book[]> {
  const response = await api.get(`/books/${bookId}/similar`);
  const data = response.data.data;
  return data.items ?? data ?? [];
}