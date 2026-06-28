import React from 'react';
import { useStore } from '../../store/useStore';
import { Card } from '../Common/Card';
import { Slider } from '../Common/Slider';
import { Input } from '../Common/Input';
import type { CountryCode } from '../../types';

interface EconomicIndicatorsProps {
  country: CountryCode;
}

export const EconomicIndicators: React.FC<EconomicIndicatorsProps> = ({ country }) => {
  const { countries, updateCountryProfile } = useStore();
  const data = countries[country]?.economicIndicators || {
    gdpGrowthRate: 3.5,
    inflationRate: 2.5,
    unemploymentRate: 5.0,
    foreignInvestmentClimate: 7,
    easeOfDoingBusinessRank: 25,
    currencyStabilityIndex: 8,
  };

  const handleChange = (field: string, value: number) => {
    updateCountryProfile(country, {
      economicIndicators: { ...data, [field]: value },
    });
  };

  return (
    <Card title="Economic Indicators">
      <div className="space-y-6">
        <Slider
          label="GDP Growth Rate (%)"
          value={data.gdpGrowthRate}
          min={-5}
          max={10}
          step={0.1}
          onChange={(value) => handleChange('gdpGrowthRate', value)}
          unit="%"
        />
        
        <Slider
          label="Inflation Rate (%)"
          value={data.inflationRate}
          min={0}
          max={20}
          step={0.1}
          onChange={(value) => handleChange('inflationRate', value)}
          unit="%"
        />
        
        <Slider
          label="Unemployment Rate (%)"
          value={data.unemploymentRate}
          min={0}
          max={20}
          step={0.1}
          onChange={(value) => handleChange('unemploymentRate', value)}
          unit="%"
        />
        
        <Slider
          label="Foreign Investment Climate (1-10)"
          value={data.foreignInvestmentClimate}
          min={1}
          max={10}
          step={0.5}
          onChange={(value) => handleChange('foreignInvestmentClimate', value)}
        />
        
        <Input
          label="Ease of Doing Business Rank"
          type="number"
          value={data.easeOfDoingBusinessRank}
          onChange={(value) => handleChange('easeOfDoingBusinessRank', value)}
        />
        
        <Slider
          label="Currency Stability Index (1-10)"
          value={data.currencyStabilityIndex}
          min={1}
          max={10}
          step={0.5}
          onChange={(value) => handleChange('currencyStabilityIndex', value)}
        />
      </div>
    </Card>
  );
};
