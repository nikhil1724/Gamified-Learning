import { createContext, useCallback, useContext, useMemo } from "react";

const ThemeContext = createContext({
  theme: "light",
  setTheme: () => {},
  toggleTheme: () => {},
});

// Light theme only - no switching
export const ThemeProvider = ({ children }) => {
  const theme = "light";

  const setTheme = useCallback(() => {
    // No-op - theme is always light
  }, []);

  const toggleTheme = useCallback(() => {
    // No-op - theme is always light
  }, []);

  const value = useMemo(
    () => ({ theme, setTheme, toggleTheme }),
    []
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => useContext(ThemeContext);
