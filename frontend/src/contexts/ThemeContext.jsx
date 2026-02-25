import { createContext, useContext, useEffect, useMemo } from 'react';
import { useAppStore } from '../stores/appStore';
import lightTheme from '../theme/lightTheme';
import darkTheme from '../theme/darkTheme';

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const themeMode = useAppStore((s) => s.theme);
  const setTheme = useAppStore((s) => s.setTheme);
  const toggleTheme = useAppStore((s) => s.toggleTheme);

  const isDark = themeMode === 'dark';
  const antdTheme = isDark ? darkTheme : lightTheme;

  // Sync data-theme attribute and color-scheme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeMode);
    document.documentElement.style.colorScheme = themeMode;
  }, [themeMode]);

  // On first mount: if no persisted preference, use system preference
  useEffect(() => {
    const stored = localStorage.getItem('ba-qa-app-storage');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed?.state?.theme) return; // Already has a saved preference
      } catch { /* ignore */ }
    }
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark) setTheme('dark');
  }, [setTheme]);

  const value = useMemo(
    () => ({ themeMode, isDark, antdTheme, toggleTheme }),
    [themeMode, isDark, antdTheme, toggleTheme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}
