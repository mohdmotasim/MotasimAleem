export type CountryCode = 
  | 'UAE' | 'SAUDI' | 'QATAR' | 'MALAYSIA' | 'TURKEY' 
  | 'JORDAN' | 'OMAN' | 'BAHRAIN' | 'INDONESIA' | 'MOROCCO' | 'KUWAIT';

export type Currency = 'USD' | 'INR' | 'LOCAL';

export type RiskAppetite = 'Conservative' | 'Moderate' | 'Aggressive';

export interface EconomicIndicators {
  gdpGrowthRate: number;
  inflationRate: number;
  unemploymentRate: number;
  foreignInvestmentClimate: number;
  easeOfDoingBusinessRank: number;
  currencyStabilityIndex: number;
}

export interface LivingStandards {
  healthcareQuality: number;
  educationSystem: number;
  publicSafety: number;
  infrastructure: number;
  costOfLivingIndex: number;
  culturalAlignmentScore: number;
}

export interface PolicyUpdate {
  residencyLawChanges: string;
  foreignOwnershipRules: string;
  taxPolicyChanges: string;
  laborLawUpdates: string;
  lastUpdated: string;
  status: 'Favorable' | 'Neutral' | 'Restrictive';
}

export interface CountryProfile {
  code: CountryCode;
  name: string;
  flag: string;
  economicIndicators: EconomicIndicators;
  livingStandards: LivingStandards;
  policyUpdates: PolicyUpdate;
  geopoliticalRiskScore: number;
  geopoliticalRiskNotes: string;
}

export interface VisaPathway {
  type: 'Employment' | 'Investor' | 'SkilledWorker' | 'Family';
  eligibilityCriteria: string[];
  requiredDocuments: DocumentStatus[];
  processingTime: string;
  governmentFeeUSD: number;
  dependentInclusionRules: string;
  pathToResidencyYears: number;
  citizenshipPossibility: 'Yes' | 'No' | 'Conditional';
}

export interface DocumentStatus {
  name: string;
  status: 'complete' | 'pending';
}

export interface DocumentChecklist {
  passportValidity: boolean;
  policeClearanceCertificate: boolean;
  educationalCertificatesAttestation: boolean;
  marriageCertificateAttestation: boolean;
  medicalFitnessCertificate: boolean;
  employmentContract: boolean;
  mofaAttestation: boolean;
  apostilleProcess: boolean;
}

export interface RelocationCosts {
  visaLegalFeesUSD: number;
  airFreightShippingUSD: number;
  housingDepositUSD: number;
  schoolAdmissionFeesUSD: number;
  vehicleSetupUSD: number;
  emergencyFundUSD: number;
  safetyBufferEnabled: boolean;
}

export interface MonthlyBudget {
  housingRentUSD: number;
  groceriesFoodUSD: number;
  schoolFeesUSD: number;
  transportUSD: number;
  utilitiesUSD: number;
  healthcareInsuranceUSD: number;
  remittancesToIndiaUSD: number;
  savingsTargetPercent: number;
}

export interface SavingsTracker {
  currentSavingsUSD: number;
  monthlySavingsRateUSD: number;
  projectedSavings: {
    year1: number;
    year3: number;
    year5: number;
    year8: number;
  };
}

export interface SalaryBenchmark {
  country: CountryCode;
  averageSapSalaryUSD: number;
  vistexPremiumPercent: number;
  netAfterTaxUSD: number;
  estimatedSavingsRate: number;
}

export interface JobMarketData {
  demandLevel: 'High' | 'Medium' | 'Low';
  topIndustries: string[];
  topSystemIntegrators: string[];
  remoteWorkPossibility: 'Yes' | 'Hybrid' | 'No';
  languageBarrier: 'EnglishOnly' | 'ArabicRequired' | 'BilingualPremium';
  indianCommunityScore: number;
  opportunityScore: number;
  jobSearchPlatforms: { name: string; url: string }[];
}

export interface GrowthForecast {
  visionPlanProgress: number;
  infrastructureInvestment: number;
  techSectorGrowth: number;
  politicalStability: number;
  youthDemographicDividend: number;
  digitalEconomyReadiness: number;
}

export interface AIAnalysis {
  country: CountryCode;
  economicOutlook: string;
  topRisks: string[];
  topOpportunities: string[];
  recommendedTimeline: string;
  verdict: 'Favorable' | 'Neutral' | 'Avoid';
  lastGenerated: string;
}

export interface Milestone {
  year: number;
  goals: string;
  progress: number;
}

export interface UserSettings {
  targetRelocationYear: number;
  familySize: number;
  currentSavingsUSD: number;
  riskAppetite: RiskAppetite;
  preferredCurrency: Currency;
  exchangeRateUSDToINR: number;
}

export interface RefreshData {
  lastFullRefresh: string;
  monthlyChecklist: {
    policyChanges: boolean;
    newVisaRules: boolean;
    salaryMarketData: boolean;
    aiReanalysis: boolean;
    geopoliticalUpdates: boolean;
  };
}

export interface AppData {
  countries: Record<CountryCode, CountryProfile>;
  visaPathways: Record<CountryCode, VisaPathway[]>;
  documentChecklist: DocumentChecklist;
  relocationCosts: RelocationCosts;
  monthlyBudget: MonthlyBudget;
  savingsTracker: SavingsTracker;
  salaryBenchmarks: SalaryBenchmark[];
  jobMarketData: Record<CountryCode, JobMarketData>;
  growthForecasts: Record<CountryCode, GrowthForecast>;
  aiAnalyses: Record<CountryCode, AIAnalysis | null>;
  milestones: Milestone[];
  settings: UserSettings;
  refreshData: RefreshData;
}
