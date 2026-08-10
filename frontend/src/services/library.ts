import { api } from "./api";

export type LibraryStatus =
  | "want_to_read"
  | "currently_reading"
  | "read"
  | "dnf";

export type LibraryItem = {
  id: string;
  user_id: string;
  book_id: string;
  content_id: string;
  status: LibraryStatus;
  current_page: number;
  total_pages: number | null;
  started_reading_at: string | null;
  finished_reading_at: string | null;
  notes: string | null;
  is_favorite: boolean;
  added_at: string;
  updated_at: string;
  title: string | null;
  cover_url: string | null;
  authors: string[] | null;
};

export type MyLibraryResponse = {
  total: number;
  limit: number;
  offset: number;
  results: LibraryItem[];
};

export type UpdateLibraryInput = {
  status?: LibraryStatus;
  current_page?: number;
  total_pages?: number;
  notes?: string | null;
  is_favorite?: boolean;
};

export async function getMyLibrary(
  status?: LibraryStatus,
  limit = 20,
  offset = 0
): Promise<MyLibraryResponse> {
  const params: Record<string, string | number> = { limit, offset };
  if (status) params.status = status;
  const response = await api.get("/library", { params });
  return response.data.data as MyLibraryResponse;
}

export async function addToLibrary(
  content_id: string,
  status: LibraryStatus = "want_to_read"
): Promise<LibraryItem> {
  const response = await api.post("/library", { content_id, status });
  return response.data.data as LibraryItem;
}

export async function removeFromLibrary(content_id: string): Promise<void> {
  await api.delete(`/library/${encodeURIComponent(content_id)}`);
}

export async function updateLibraryEntry(
  content_id: string,
  updates: UpdateLibraryInput
): Promise<LibraryItem> {
  const response = await api.patch(
    `/library/${encodeURIComponent(content_id)}`,
    updates
  );
  return response.data.data as LibraryItem;
}

export async function getLibraryItem(
  content_id: string
): Promise<LibraryItem | null> {
  try {
    const response = await api.get(
      `/library/${encodeURIComponent(content_id)}`
    );
    return response.data.data as LibraryItem;
  } catch (error: any) {
    if (error?.response?.status === 404) {
      return null;
    }
    throw error;
  }
}

export async function isInLibrary(
  content_id: string
): Promise<LibraryItem | null> {
  const library = await getMyLibrary();
  return library.results.find((item) => item.content_id === content_id) ?? null;
}