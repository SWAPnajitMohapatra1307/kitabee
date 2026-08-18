import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  LibraryItem,
  LibraryStatus,
  UpdateLibraryInput,
  getMyLibrary,
  addToLibrary,
  removeFromLibrary,
  updateLibraryEntry,
} from "../services/library";

interface LibraryStore {
  items: LibraryItem[];
  loaded: boolean;
  loading: boolean;

  load: () => Promise<void>;
  syncFromServer: () => Promise<void>;
  addOptimistic: (item: LibraryItem) => void;
  removeOptimistic: (content_id: string) => void;
  setStatusOptimistic: (content_id: string, status: LibraryStatus) => void;
  patchOptimistic: (content_id: string, updates: Partial<LibraryItem>) => void;
  getItem: (content_id: string) => LibraryItem | undefined;

  addToLibrary: (content_id: string, status?: LibraryStatus) => Promise<LibraryItem>;
  removeFromLibrary: (content_id: string) => Promise<void>;
  setStatus: (content_id: string, status: LibraryStatus) => Promise<LibraryItem>;
  updateEntry: (content_id: string, updates: UpdateLibraryInput) => Promise<LibraryItem>;
}

export const useLibraryStore = create<LibraryStore>()(
  persist(
    (set, get) => ({
      items: [],
      loaded: false,
      loading: false,

      load: async () => {
        if (get().loaded || get().loading) return;
        set({ loading: true });
        try {
          const response = await getMyLibrary(undefined, 100, 0);
          set({ items: response.results, loaded: true });
        } finally {
          set({ loading: false });
        }
      },

      syncFromServer: async () => {
        set({ loading: true });
        try {
          const response = await getMyLibrary(undefined, 100, 0);
          set({ items: response.results, loaded: true });
        } finally {
          set({ loading: false });
        }
      },

      addOptimistic: (item) => {
        set((state) => ({
          items: [
            item,
            ...state.items.filter((i) => i.content_id !== item.content_id),
          ],
        }));
      },

      removeOptimistic: (content_id) => {
        set((state) => ({
          items: state.items.filter((i) => i.content_id !== content_id),
        }));
      },

      setStatusOptimistic: (content_id, status) => {
        set((state) => ({
          items: state.items.map((i) =>
            i.content_id === content_id ? { ...i, status } : i
          ),
        }));
      },

      patchOptimistic: (content_id, updates) => {
        set((state) => ({
          items: state.items.map((i) =>
            i.content_id === content_id ? { ...i, ...updates } : i
          ),
        }));
      },

      getItem: (content_id) => {
        return get().items.find((i) => i.content_id === content_id);
      },

      addToLibrary: async (content_id, status = "want_to_read") => {
        const item = await addToLibrary(content_id, status);
        get().addOptimistic(item);
        return item;
      },

      removeFromLibrary: async (content_id) => {
        get().removeOptimistic(content_id);
        try {
          await removeFromLibrary(content_id);
        } catch (e) {
          get().syncFromServer();
          throw e;
        }
      },

      setStatus: async (content_id, status) => {
        get().setStatusOptimistic(content_id, status);
        try {
          const updated = await updateLibraryEntry(content_id, { status });
          get().addOptimistic(updated);
          return updated;
        } catch (e) {
          get().syncFromServer();
          throw e;
        }
      },

      updateEntry: async (content_id, updates) => {
        get().patchOptimistic(content_id, updates as Partial<LibraryItem>);
        try {
          const updated = await updateLibraryEntry(content_id, updates);
          get().addOptimistic(updated);
          return updated;
        } catch (e) {
          get().syncFromServer();
          throw e;
        }
      },
    }),
    {
      name: "kitabee-library",
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);