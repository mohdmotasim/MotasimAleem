import React from 'react';
import { useStore } from '../../store/useStore';
import { EconomicIndicators } from './EconomicIndicators';
import { LivingStandards } from './LivingStandards';
import { PolicyTracker } from './PolicyTracker';
import { GeopoliticalRisk } from './GeopoliticalRisk';
import type { CountryCode } from '../../types';

interface CountryProfileProps {
  country: CountryCode;
}

export const CountryProfile: React.FC<CountryProfileProps> = ({ country }) => {
  const { countries } = useStore();
  const countryData = countries[country];

  if (!countryData) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-600 dark:text-slate-400">
          Select a country to view its profile
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
          Country Profile
        </h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EconomicIndicators country={country} />
        <LivingStandards country={country} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PolicyTracker country={country} />
        <GeopoliticalRisk country={country} />
      </div>
    </div>
  );
};
