import React from 'react';
import { useStore } from '../../store/useStore';
import { Card } from '../Common/Card';
import { Slider } from '../Common/Slider';
import { TextArea } from '../Common/TextArea';
import type { CountryCode } from '../../types';

interface GeopoliticalRiskProps {
  country: CountryCode;
}

export const GeopoliticalRisk: React.FC<GeopoliticalRiskProps> = ({ country }) => {
  const { countries, updateCountryProfile } = useStore();
  const data = countries[country] || {
    geopoliticalRiskScore: 3,
    geopoliticalRiskNotes: '',
  };

  const handleScoreChange = (value: number) => {
    updateCountryProfile(country, {
      geopoliticalRiskScore: value,
    });
  };

  const handleNotesChange = (value: string) => {
    updateCountryProfile(country, {
      geopoliticalRiskNotes: value,
    });
  };

  const getRiskLevel = (score: number) => {
    if (score <= 3) return { label: 'Low', color: 'text-emerald-600 dark:text-emerald-400' };
    if (score <= 6) return { label: 'Medium', color: 'text-yellow-600 dark:text-yellow-400' };
    return { label: 'High', color: 'text-red-600 dark:text-red-400' };
  };

  const riskLevel = getRiskLevel(data.geopoliticalRiskScore);

  return (
    <Card title="Geopolitical Risk Assessment">
      <div className="space-y-6">
        <Slider
          label="Risk Score (1-10)"
          value={data.geopoliticalRiskScore}
          min={1}
          max={10}
          step={0.5}
          onChange={handleScoreChange}
        />

        <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900/50 rounded-lg">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Risk Level
          </span>
          <span className={`text-lg font-bold ${riskLevel.color}`}>
            {riskLevel.label}
          </span>
        </div>

        <TextArea
          label="Risk Notes & Analysis"
          value={data.geopoliticalRiskNotes}
          onChange={handleNotesChange}
          placeholder="Enter notes about geopolitical risks, regional tensions, political stability..."
          rows={4}
        />
      </div>
    </Card>
  );
};
