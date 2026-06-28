import React from 'react';
import { 
  Globe, 
  FileText, 
  DollarSign, 
  Briefcase, 
  TrendingUp, 
  LayoutDashboard,
  Settings,
  Menu,
  X
} from 'lucide-react';

interface SidebarProps {
  activeModule: string;
  onModuleChange: (module: string) => void;
  isCollapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeModule,
  onModuleChange,
  isCollapsed,
  onToggle,
}) => {
  const modules = [
    { id: 'country-intelligence', name: 'Country Intelligence', icon: Globe },
    { id: 'visa-tracker', name: 'Visa & Documents', icon: FileText },
    { id: 'financial-planning', name: 'Financial Planning', icon: DollarSign },
    { id: 'job-market', name: 'Job Market', icon: Briefcase },
    { id: 'growth-forecast', name: 'Growth Forecast', icon: TrendingUp },
    { id: 'command-center', name: 'Command Center', icon: LayoutDashboard },
  ];

  return (
    <div className={`fixed left-0 top-0 h-full bg-slate-900 dark:bg-slate-950 text-white transition-all duration-300 z-50 ${
      isCollapsed ? 'w-16' : 'w-64'
    }`}>
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        {!isCollapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">H</span>
            </div>
            <span className="text-xl font-bold">Hijrah</span>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-slate-800 transition-colors"
        >
          {isCollapsed ? <Menu size={20} /> : <X size={20} />}
        </button>
      </div>

      <nav className="p-4 space-y-2">
        {modules.map((module) => {
          const Icon = module.icon;
          return (
            <button
              key={module.id}
              onClick={() => onModuleChange(module.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                activeModule === module.id
                  ? 'bg-emerald-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Icon size={20} />
              {!isCollapsed && <span className="font-medium">{module.name}</span>}
            </button>
          );
        })}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700">
        <button
          onClick={() => onModuleChange('settings')}
          className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
            activeModule === 'settings'
              ? 'bg-emerald-600 text-white'
              : 'text-slate-300 hover:bg-slate-800'
          }`}
        >
          <Settings size={20} />
          {!isCollapsed && <span className="font-medium">Settings</span>}
        </button>
      </div>
    </div>
  );
};
