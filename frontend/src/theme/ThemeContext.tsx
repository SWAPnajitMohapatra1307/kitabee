import React, { ReactNode } from "react";
import { useColorScheme } from "react-native";
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { darkTheme, lightTheme, Theme } from "./tokens";
import { typography, spacing, rounded, motion } from "./typography";

type ThemeMode = "dark" | "light" | "system";

interface ThemeStore {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      mode: "system",
      setMode: (mode) => set({ mode }),
    }),
    {
      name: "kitabee-theme",
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

interface ThemeContextValue {
  theme: Theme;
  typography: typeof typography;
  spacing: typeof spacing;
  rounded: typeof rounded;
  motion: typeof motion;
  mode: ThemeMode;
  activeMode: "dark" | "light";
  setMode: (mode: ThemeMode) => void;
}

export function useTheme(): ThemeContextValue {
  const systemScheme = useColorScheme();
  const mode = useThemeStore((s) => s.mode);
  const setMode = useThemeStore((s) => s.setMode);

const activeMode: "dark" | "light" =
    mode === "system" ? (systemScheme === "light" ? "light" : "dark") : mode;
  const theme = activeMode === "dark" ? darkTheme : lightTheme;

  return {
    theme,
    typography,
    spacing,
    rounded,
    motion,
    mode,
    activeMode,
    setMode,
  };
}

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  return <>{children}</>;
}