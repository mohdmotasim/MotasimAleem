import React from 'react';
import { useStore } from '../../store/useStore';
import type { CountryCode } from '../../types';

const COUNTRIES: { code: CountryCode; name: string; flag: string }[] = [
  { code: 'UAE', name: 'United Arab Emirates', flag: '🇦🇪' },
  { code: 'SAUDI', name: 'Saudi Arabia', flag: '🇸🇦' },
  { code: 'QATAR', name: 'Qatar', flag: '🇶🇦' },
  { code: 'MALAYSIA', name: 'Malaysia', flag: '🇲🇾' },
  { code: 'TURKEY', name: 'Turkey', flag: '🇹🇷' },
  { code: 'JORDAN', name: 'Jordan', flag: '🇯🇴' },
  { code: 'OMAN', name: 'Oman', flag: '🇴🇲' },
  { code: 'BAHRAIN', name: 'Bahrain', flag: '🇧🇭' },
  { code: 'INDONESIA', name: 'Indonesia', flag: '🇮🇩' },
  { code: 'MOROCCO', name: 'Morocco', flag: '🇲🇦' },
  { code: 'KUWAIT', name: 'Kuwait', flag: '🇰🇼' },
];

export const CountrySelector: React.FC = () => {
  const { selectedCountry, setSelectedCountry, countries } = useStore();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {COUNTRIES.map((country) => (
        <button
          key={country.code}
          onClick={() => setSelectedCountry(country.code)}
          className={`p-4 rounded-xl border-2 transition-all ${
            selectedCountry === country.code
              ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
              : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-emerald-300'
          }`}
        >
          <div className="flex items-center space-x-3">
            <span className="text-3xl">{country.flag}</span>
            <div className="text-left">
              <p className="font-semibold text-slate-900 dark:text-white">
                {country.name}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {country.code}
              </p>
            </div>
          </div>
          {countries[country.code] && (
            <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
              <p className="text-xs text-slate-600 dark:text-slate-400">
                Data saved
              </p>
            </div>
          )}
        </button>
      ))}
    </div>
  );
};
