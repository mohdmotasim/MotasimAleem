import React from 'react';
import { Moon, Sun, Download, Upload } from 'lucide-react';
import { useStore } from '../../store/useStore';

interface HeaderProps {
  onExport: () => void;
  onImport: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onExport, onImport }) => {
  const { settings, updateSettings } = useStore();

  const toggleDarkMode = () => {
    const newMode = settings.preferredCurrency === 'USD' ? 'INR' : 'USD';
    updateSettings({ preferredCurrency: newMode as any });
  };

  return (
    <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Hijrah Strategic Planner
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Your relocation planning companion
          </p>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm font-medium text-slate-900 dark:text-white">
              Target Year: {settings.targetRelocationYear}
            </p>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Family Size: {settings.familySize}
            </p>
          </div>

          <div className="h-8 w-px bg-slate-300 dark:bg-slate-600" />

          <button
            onClick={onExport}
            className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
            title="Export Data"
          >
            <Download size={20} />
          </button>

          <button
            onClick={onImport}
            className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
            title="Import Data"
          >
            <Upload size={20} />
          </button>
        </div>
      </div>
    </header>
  );
};
