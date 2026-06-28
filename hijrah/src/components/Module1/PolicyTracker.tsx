import React from 'react';
import { useStore } from '../../store/useStore';
import { Card } from '../Common/Card';
import { TextArea } from '../Common/TextArea';
import { Badge } from '../Common/Badge';
import type { CountryCode } from '../../types';

interface PolicyTrackerProps {
  country: CountryCode;
}

export const PolicyTracker: React.FC<PolicyTrackerProps> = ({ country }) => {
  const { countries, updateCountryProfile } = useStore();
  const data = countries[country]?.policyUpdates || {
    residencyLawChanges: '',
    foreignOwnershipRules: '',
    taxPolicyChanges: '',
    laborLawUpdates: '',
    lastUpdated: new Date().toISOString(),
    status: 'Neutral' as const,
  };

  const handleChange = (field: string, value: string) => {
    updateCountryProfile(country, {
      policyUpdates: { ...data, [field]: value },
    });
  };

  const handleStatusChange = (status: 'Favorable' | 'Neutral' | 'Restrictive') => {
    updateCountryProfile(country, {
      policyUpdates: { ...data, status, lastUpdated: new Date().toISOString() },
    });
  };

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'Favorable': return 'success';
      case 'Neutral': return 'warning';
      case 'Restrictive': return 'danger';
      default: return 'info';
    }
  };

  return (
    <Card title="Governance & Policy Tracker">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Current Status
          </span>
          <div className="flex space-x-2">
            {(['Favorable', 'Neutral', 'Restrictive'] as const).map((status) => (
              <button
                key={status}
                onClick={() => handleStatusChange(status)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  data.status === status
                    ? 'bg-emerald-600 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                }`}
              >
                {status === 'Favorable' && '🟢'}
                {status === 'Neutral' && '🟡'}
                {status === 'Restrictive' && '🔴'} {status}
              </button>
            ))}
          </div>
        </div>

        <TextArea
          label="Residency Law Changes"
          value={data.residencyLawChanges}
          onChange={(value) => handleChange('residencyLawChanges', value)}
          placeholder="Enter recent changes to residency laws..."
          rows={3}
        />

        <TextArea
          label="Foreign Ownership Rules"
          value={data.foreignOwnershipRules}
          onChange={(value) => handleChange('foreignOwnershipRules', value)}
          placeholder="Enter updates to foreign ownership regulations..."
          rows={3}
        />

        <TextArea
          label="Tax Policy Changes"
          value={data.taxPolicyChanges}
          onChange={(value) => handleChange('taxPolicyChanges', value)}
          placeholder="Enter tax policy updates..."
          rows={3}
        />

        <TextArea
          label="Labor Law Updates"
          value={data.laborLawUpdates}
          onChange={(value) => handleChange('laborLawUpdates', value)}
          placeholder="Enter labor law changes..."
          rows={3}
        />

        <div className="flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
          <Badge variant={getStatusVariant(data.status)}>{data.status}</Badge>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            Last Updated: {new Date(data.lastUpdated).toLocaleDateString()}
          </span>
        </div>
      </div>
    </Card>
  );
};
