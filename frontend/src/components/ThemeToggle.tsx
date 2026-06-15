import { Sun, Moon } from 'lucide-react';

interface ThemeToggleProps {
  theme: 'dark' | 'light';
  onToggle: () => void;
}

export default function ThemeToggle({ theme, onToggle }: ThemeToggleProps) {
  return (
    <button
      onClick={onToggle}
      className="p-1.5 rounded-lg hover:bg-dark-700 transition-colors"
      title={theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
    >
      {theme === 'dark' ? (
        <Sun className="w-4 h-4 text-dark-300" />
      ) : (
        <Moon className="w-4 h-4 text-dark-300" />
      )}
    </button>
  );
}
