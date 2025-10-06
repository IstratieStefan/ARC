import React, { useContext } from 'react';
import { ThemeContext } from './ThemeProvider';

const ColorSelector: React.FC = () => {
  const { accentColor, setAccentColor } = useContext(ThemeContext);
  
  const colors = [
    { id: 'blue', label: 'Blue', color: '#007aff' },
    { id: 'green', label: 'Green', color: '#34c759' },
    { id: 'purple', label: 'Purple', color: '#af52de' },
    { id: 'orange', label: 'Orange', color: '#ff9500' },
    { id: 'red', label: 'Red', color: '#ff3b30' },
  ] as const;

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm font-medium text-gray-700">Accent:</span>
      <div className="flex space-x-2">
        {colors.map(({ id, color }) => (
          <button
            key={id}
            className={`w-6 h-6 rounded-full transition-transform ${
              accentColor === id ? 'ring-2 ring-offset-2 scale-110' : 'hover:scale-105'
            }`}
            style={{ backgroundColor: color }}
            aria-label={`Set accent color to ${id}`}
            onClick={() => setAccentColor(id as any)}
          />
        ))}
      </div>
    </div>
  );
};

export default ColorSelector;