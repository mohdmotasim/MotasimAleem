export const calculateRelocationTotal = (
  costs: {
    visaLegalFeesUSD: number;
    airFreightShippingUSD: number;
    housingDepositUSD: number;
    schoolAdmissionFeesUSD: number;
    vehicleSetupUSD: number;
    emergencyFundUSD: number;
    safetyBufferEnabled: boolean;
  }
): number => {
  const baseTotal =
    costs.visaLegalFeesUSD +
    costs.airFreightShippingUSD +
    costs.housingDepositUSD +
    costs.schoolAdmissionFeesUSD +
    costs.vehicleSetupUSD +
    costs.emergencyFundUSD;

  return costs.safetyBufferEnabled ? baseTotal * 1.2 : baseTotal;
};

export const calculateMonthlyTotal = (
  budget: {
    housingRentUSD: number;
    groceriesFoodUSD: number;
    schoolFeesUSD: number;
    transportUSD: number;
    utilitiesUSD: number;
    healthcareInsuranceUSD: number;
    remittancesToIndiaUSD: number;
    savingsTargetPercent: number;
  }
): { totalUSD: number; savingsUSD: number } => {
  const expenses =
    budget.housingRentUSD +
    budget.groceriesFoodUSD +
    budget.schoolFeesUSD +
    budget.transportUSD +
    budget.utilitiesUSD +
    budget.healthcareInsuranceUSD +
    budget.remittancesToIndiaUSD;

  const savingsUSD = expenses * (budget.savingsTargetPercent / 100);
  const totalUSD = expenses + savingsUSD;

  return { totalUSD, savingsUSD };
};

export const calculateProjectedSavings = (
  currentSavings: number,
  monthlySavings: number
): { year1: number; year3: number; year5: number; year8: number } => {
  return {
    year1: currentSavings + monthlySavings * 12,
    year3: currentSavings + monthlySavings * 36,
    year5: currentSavings + monthlySavings * 60,
    year8: currentSavings + monthlySavings * 96,
  };
};

export const calculateOpportunityScore = (
  demandLevel: 'High' | 'Medium' | 'Low',
  salaryScore: number,
  communityScore: number,
  englishFriendly: boolean
): number => {
  const demandScore = demandLevel === 'High' ? 10 : demandLevel === 'Medium' ? 6 : 3;
  const englishScore = englishFriendly ? 10 : 5;

  return (
    demandScore * 0.4 +
    salaryScore * 0.3 +
    communityScore * 0.2 +
    englishScore * 0.1
  );
};

export const calculateLivingStandardsScore = (
  livingStandards: {
    healthcareQuality: number;
    educationSystem: number;
    publicSafety: number;
    infrastructure: number;
    costOfLivingIndex: number;
    culturalAlignmentScore: number;
  }
): number => {
  const baseScore =
    (livingStandards.healthcareQuality +
      livingStandards.educationSystem +
      livingStandards.publicSafety +
      livingStandards.infrastructure +
      livingStandards.culturalAlignmentScore) /
    5;

  // Adjust for cost of living (lower is better, base is 100)
  const costAdjustment = Math.max(0, (150 - livingStandards.costOfLivingIndex) / 50);

  return Math.min(10, baseScore + costAdjustment);
};
