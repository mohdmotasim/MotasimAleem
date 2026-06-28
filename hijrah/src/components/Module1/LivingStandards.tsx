import React from 'react';
import { useStore } from '../../store/useStore';
import { Card } from '../Common/Card';
import { Slider } from '../Common/Slider';
import type { CountryCode } from '../../types';

interface LivingStandardsProps {
  country: CountryCode;
}

export const LivingStandards: React.FC<LivingStandardsProps> = ({ country }) => {
  const { countries, updateCountryProfile } = useStore();
  const data = countries[country]?.livingStandards || {
    healthcareQuality: 7,
    educationSystem: 7,
    publicSafety: 8,
    infrastructure: 8,
    costOfLivingIndex: 120,
    culturalAlignmentScore: 8,
  };

  const handleChange = (field: string, value: number) => {
    updateCountryProfile(country, {
      livingStandards: { ...data, [field]: value },
    });
  };

  return (
    <Card title="Living Standards Index">
      <div className="space-y-6">
        <Slider
          label="Healthcare Quality (1-10)"
          value={data.healthcareQuality}
          min={1}
          max={10}
          step={0.5}
          onChange={(value) => handleChange('healthcareQuality', value)}
        />
        
        <Slider
          label="Education System (1-10)"
          value={data.educationSystem}
          min={1}
          max={10}
          step={0.5}
          onChange={(value) => handleChange('educationSystem', value)}
        />
        
        <Slider
          label="Public Safety (1-10)"
          value={data.publicSafety}
          min={1}
          max={10}
          step={0.5}
          onChange={(value) => handleChange('publicSafety', value)}
        />
        
        <Slider
          label="Infrastructure (1-10)"
          value={data.infrastructure}
          min={1}
          max={10}
          step={0.5}
          onChange={(value) => handleChange('infrastructure', value)}
        />
        
        <Slider
          label="Cost of Living Index (Hyderabad = 100)"
          value={data.costOfLivingIndex}
          min={50}
          max={250}
          step={5}
          onChange={(value) => handleChange('costOfLivingIndex', value)}
        />
        
        <Slider
          label="Religious/Cultural Alignment for Indian Muslims (1-10)"
          value={data.culturalAlignmentScore}
          min={1}
          max={10}
          step={0.5}
          onChange={(value) => handleChange('culturalAlignmentScore', value)}
        />
      </div>
    </Card>
  );
};
