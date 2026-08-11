import { api } from "./api";

export type Rating = {
  id: string;
  user_id: string;
  book_id: string;
  rating: number;
  review_title: string | null;
  review_text: string | null;
  is_spoiler: boolean;
  helpful_count: number;
  created_at: string;
  updated_at: string;
};

export type RatingInput = {
  rating: number;
  review_title?: string | null;
  review_text?: string | null;
  is_spoiler?: boolean;
};

export async function rateBook(
  contentId: string,
  input: RatingInput
): Promise<Rating> {
  const response = await api.post(
    `/books/${encodeURIComponent(contentId)}/ratings`,
    input
  );
  return response.data.data as Rating;
}

export async function getMyRating(contentId: string): Promise<Rating | null> {
  try {
    const response = await api.get(
      `/books/${encodeURIComponent(contentId)}/ratings/me`
    );
    return response.data.data as Rating;
  } catch (error: any) {
    if (error?.response?.status === 404) {
      return null;
    }
    throw error;
  }
}

export async function deleteMyRating(contentId: string): Promise<void> {
  await api.delete(`/books/${encodeURIComponent(contentId)}/ratings/me`);
}