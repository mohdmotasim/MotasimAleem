import React, { useState } from 'react';
import { Sidebar } from './components/Layout/Sidebar';
import { Header } from './components/Layout/Header';
import { CountrySelector } from './components/Module1/CountrySelector';
import { CountryProfile } from './components/Module1/CountryProfile';
import { useStore } from './store/useStore';

function App() {
  const [activeModule, setActiveModule] = useState('country-intelligence');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { selectedCountry, exportData, importData } = useStore();

  const handleExport = () => {
    const data = exportData();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hijrah-backup-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          importData(event.target?.result as string);
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  const renderModule = () => {
    switch (activeModule) {
      case 'country-intelligence':
        return (
          <div className="space-y-6">
            <CountrySelector />
            {selectedCountry && <CountryProfile country={selectedCountry} />}
          </div>
        );
      case 'visa-tracker':
        return (
          <div className="text-center py-12">
            <p className="text-slate-600 dark:text-slate-400">
              Visa & Documentation Tracker - Coming Soon
            </p>
          </div>
        );
      case 'financial-planning':
        return (
          <div className="text-center py-12">
            <p className="text-slate-600 dark:text-slate-400">
              Financial Planning Module - Coming Soon
            </p>
          </div>
        );
      case 'job-market':
        return (
          <div className="text-center py-12">
            <p className="text-slate-600 dark:text-slate-400">
              Job Market Intelligence - Coming Soon
            </p>
          </div>
        );
      case 'growth-forecast':
        return (
          <div className="text-center py-12">
            <p className="text-slate-600 dark:text-slate-400">
              Growth Forecast Module - Coming Soon
            </p>
          </div>
        );
      case 'command-center':
        return (
          <div className="text-center py-12">
            <p className="text-slate-600 dark:text-slate-400">
              Command Center - Coming Soon
            </p>
          </div>
        );
      case 'settings':
        return (
          <div className="text-center py-12">
            <p className="text-slate-600 dark:text-slate-400">
              Settings - Coming Soon
            </p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <Sidebar
        activeModule={activeModule}
        onModuleChange={setActiveModule}
        isCollapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      
      <div className={`transition-all duration-300 ${
        sidebarCollapsed ? 'ml-16' : 'ml-64'
      }`}>
        <Header onExport={handleExport} onImport={handleImport} />
        
        <main className="p-6">
          {renderModule()}
        </main>
      </div>
    </div>
  );
}

export default App;
