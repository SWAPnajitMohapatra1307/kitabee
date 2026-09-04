import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { clearAuthToken } from "../services/api";

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string | null;
  bio?: string | null;
  onboarding_completed: boolean;
  email_verified: boolean;
  created_at: string;
  updated_at: string;
}

interface UserStore {
  user: User | null;
  isAuthenticated: boolean;
  hasHydrated: boolean;
  setUser: (user: User | null) => void;
  setHasHydrated: (value: boolean) => void;
  logout: () => Promise<void>;
}

export const useUserStore = create<UserStore>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      hasHydrated: false,

      setUser: (user) =>
        set({
          user,
          isAuthenticated: !!user,
        }),

      setHasHydrated: (value) => set({ hasHydrated: value }),

      logout: async () => {
        await clearAuthToken();
        set({ user: null, isAuthenticated: false });
      },
    }),
    {
      name: "kitabee-user",
      storage: createJSONStorage(() => AsyncStorage),
      // Only persist what matters for routing
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);