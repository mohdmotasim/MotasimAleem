import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AppData, CountryCode, UserSettings, RefreshData } from '../types';

const defaultSettings: UserSettings = {
  targetRelocationYear: new Date().getFullYear() + 5,
  familySize: 4,
  currentSavingsUSD: 50000,
  riskAppetite: 'Moderate',
  preferredCurrency: 'USD',
  exchangeRateUSDToINR: 83.5,
};

const defaultRefreshData: RefreshData = {
  lastFullRefresh: new Date().toISOString(),
  monthlyChecklist: {
    policyChanges: false,
    newVisaRules: false,
    salaryMarketData: false,
    aiReanalysis: false,
    geopoliticalUpdates: false,
  },
};

interface StoreState extends AppData {
  selectedCountry: CountryCode | null;
  setSelectedCountry: (country: CountryCode | null) => void;
  updateCountryProfile: (country: CountryCode, data: Partial<AppData['countries'][CountryCode]>) => void;
  updateVisaPathways: (country: CountryCode, pathways: any[]) => void;
  updateDocumentChecklist: (checklist: Partial<AppData['documentChecklist']>) => void;
  updateRelocationCosts: (costs: Partial<AppData['relocationCosts']>) => void;
  updateMonthlyBudget: (budget: Partial<AppData['monthlyBudget']>) => void;
  updateSavingsTracker: (tracker: Partial<AppData['savingsTracker']>) => void;
  updateJobMarketData: (country: CountryCode, data: Partial<AppData['jobMarketData'][CountryCode]>) => void;
  updateGrowthForecast: (country: CountryCode, data: Partial<AppData['growthForecasts'][CountryCode]>) => void;
  updateAIAnalysis: (country: CountryCode, analysis: AppData['aiAnalyses'][CountryCode]) => void;
  updateSettings: (settings: Partial<UserSettings>) => void;
  updateRefreshData: (data: Partial<RefreshData>) => void;
  updateMilestone: (index: number, milestone: Partial<AppData['milestones'][0]>) => void;
  exportData: () => string;
  importData: (jsonData: string) => void;
}

const createInitialData = (): AppData => ({
  countries: {} as Record<CountryCode, any>,
  visaPathways: {} as Record<CountryCode, any[]>,
  documentChecklist: {
    passportValidity: false,
    policeClearanceCertificate: false,
    educationalCertificatesAttestation: false,
    marriageCertificateAttestation: false,
    medicalFitnessCertificate: false,
    employmentContract: false,
    mofaAttestation: false,
    apostilleProcess: false,
  },
  relocationCosts: {
    visaLegalFeesUSD: 2000,
    airFreightShippingUSD: 5000,
    housingDepositUSD: 10000,
    schoolAdmissionFeesUSD: 3000,
    vehicleSetupUSD: 15000,
    emergencyFundUSD: 30000,
    safetyBufferEnabled: true,
  },
  monthlyBudget: {
    housingRentUSD: 2000,
    groceriesFoodUSD: 800,
    schoolFeesUSD: 1500,
    transportUSD: 400,
    utilitiesUSD: 300,
    healthcareInsuranceUSD: 500,
    remittancesToIndiaUSD: 1000,
    savingsTargetPercent: 20,
  },
  savingsTracker: {
    currentSavingsUSD: 50000,
    monthlySavingsRateUSD: 2000,
    projectedSavings: {
      year1: 74000,
      year3: 122000,
      year5: 170000,
      year8: 242000,
    },
  },
  salaryBenchmarks: [],
  jobMarketData: {} as Record<CountryCode, any>,
  growthForecasts: {} as Record<CountryCode, any>,
  aiAnalyses: {} as Record<CountryCode, any>,
  milestones: [
    { year: 1, goals: '', progress: 0 },
    { year: 3, goals: '', progress: 0 },
    { year: 5, goals: '', progress: 0 },
  ],
  settings: defaultSettings,
  refreshData: defaultRefreshData,
});

export const useStore = create<StoreState>()(
  persist(
    (set) => ({
      ...createInitialData(),
      selectedCountry: null,
      
      setSelectedCountry: (country) => set({ selectedCountry: country }),
      
      updateCountryProfile: (country, data) =>
        set((state) => ({
          countries: {
            ...state.countries,
            [country]: { ...state.countries[country], ...data },
          },
        })),
      
      updateVisaPathways: (country, pathways) =>
        set((state) => ({
          visaPathways: {
            ...state.visaPathways,
            [country]: pathways,
          },
        })),
      
      updateDocumentChecklist: (checklist) =>
        set((state) => ({
          documentChecklist: { ...state.documentChecklist, ...checklist },
        })),
      
      updateRelocationCosts: (costs) =>
        set((state) => ({
          relocationCosts: { ...state.relocationCosts, ...costs },
        })),
      
      updateMonthlyBudget: (budget) =>
        set((state) => ({
          monthlyBudget: { ...state.monthlyBudget, ...budget },
        })),
      
      updateSavingsTracker: (tracker) =>
        set((state) => ({
          savingsTracker: { ...state.savingsTracker, ...tracker },
        })),
      
      updateJobMarketData: (country, data) =>
        set((state) => ({
          jobMarketData: {
            ...state.jobMarketData,
            [country]: { ...state.jobMarketData[country], ...data },
          },
        })),
      
      updateGrowthForecast: (country, data) =>
        set((state) => ({
          growthForecasts: {
            ...state.growthForecasts,
            [country]: { ...state.growthForecasts[country], ...data },
          },
        })),
      
      updateAIAnalysis: (country, analysis) =>
        set((state) => ({
          aiAnalyses: {
            ...state.aiAnalyses,
            [country]: analysis,
          },
        })),
      
      updateSettings: (settings) =>
        set((state) => ({
          settings: { ...state.settings, ...settings },
        })),
      
      updateRefreshData: (data) =>
        set((state) => ({
          refreshData: { ...state.refreshData, ...data },
        })),
      
      updateMilestone: (index, milestone) =>
        set((state) => {
          const newMilestones = [...state.milestones];
          newMilestones[index] = { ...newMilestones[index], ...milestone };
          return { milestones: newMilestones };
        }),
      
      exportData: () => {
        const state = useStore.getState();
        return JSON.stringify(state, null, 2);
      },
      
      importData: (jsonData) => {
        try {
          const data = JSON.parse(jsonData);
          set(data);
        } catch (error) {
          console.error('Failed to import data:', error);
        }
      },
    }),
    {
      name: 'hijrah-storage',
    }
  )
);
