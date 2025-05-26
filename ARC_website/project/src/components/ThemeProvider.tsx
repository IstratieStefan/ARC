import { createContext, useState, useEffect, type ReactNode } from 'react';

type AccentColor = 'blue' | 'green' | 'purple' | 'orange' | 'red';

interface ThemeContextType {
  accentColor: AccentColor;
  setAccentColor: (color: AccentColor) => void;
}

export const ThemeContext = createContext<ThemeContextType>({
  accentColor: 'blue',
  setAccentColor: () => {},
});

interface ThemeProviderProps {
  children: ReactNode;
}

const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [accentColor, setAccentColor] = useState<AccentColor>('blue');

  useEffect(() => {
    // Load saved preference from localStorage if available
    const savedColor = localStorage.getItem('accentColor') as AccentColor | null;
    if (savedColor && ['blue', 'green', 'purple', 'orange', 'red'].includes(savedColor)) {
      setAccentColor(savedColor);
    }
  }, []);

  useEffect(() => {
    // Set data attribute on document element
    document.documentElement.setAttribute('data-accent', accentColor);
    // Save preference to localStorage
    localStorage.setItem('accentColor', accentColor);
  }, [accentColor]);

  return (
    <ThemeContext.Provider value={{ accentColor, setAccentColor }}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;