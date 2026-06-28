# Hijrah Strategic Planner

A comprehensive relocation planning dashboard for Muslim professionals from India, specifically designed for SAP SD/Vistex consultants planning to move to Muslim-majority countries within 5–8 years.

## Tech Stack

- **React 18 + TypeScript** - UI library with type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - Lightweight state management with persistence
- **Recharts** - Data visualization library
- **React Router v6** - Client-side routing
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icon library
- **Anthropic Claude API** - AI-powered analysis (optional)

## Features

### Module 1: Country Intelligence Hub ✅
- Country selector with 11 Muslim-majority countries
- Economic indicators (GDP, inflation, unemployment, etc.)
- Living standards index with composite scoring
- Governance & policy tracker with status badges
- Geopolitical risk assessment

### Module 2: Visa & Documentation Tracker (Coming Soon)
- Visa pathway cards for different visa types
- Document preparation checklist
- Progress tracking for document status

### Module 3: Financial Planning Module (Coming Soon)
- One-time relocation cost estimator
- Monthly sustain budget calculator
- Savings accumulation tracker with charts
- SAP/Vistex salary benchmarks per country

### Module 4: Job Market Intelligence (Coming Soon)
- Job market data per country
- Opportunity score calculation
- Job search platform links

### Module 5: Growth Forecast Module (Coming Soon)
- Country future index with radar charts
- AI analysis panel using Claude API
- 5–8 year horizon analysis

### Module 6: Monthly Refresh Dashboard (Coming Soon)
- Summary comparison table
- Top 3 recommendation engine
- Personal milestone tracker
- Monthly refresh checklist

### Additional Features
- 🌙 Dark mode support
- 📱 Fully responsive design with collapsible sidebar
- 💾 LocalStorage persistence for all data
- 📤 Export/Import data as JSON
- 💱 Currency toggle (USD/INR/Local)
- 🖨️ Print/PDF export per country profile

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Navigate to the project directory:
```bash
cd C:\Users\HP\OneDrive\Desktop\Bis\hijrah
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Add your Anthropic API key (optional, for AI features):
```
VITE_ANTHROPIC_API_KEY=your_api_key_here
```

### Development

Run the development server:
```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to view the application in your browser.

### Build for Production

Create an optimized production build:
```bash
npm run build
```

The built files will be in the `dist` directory.

### Preview Production Build

Preview the production build locally:
```bash
npm run preview
```

## Project Structure

```
hijrah/
├── src/
│   ├── components/
│   │   ├── Layout/          # Sidebar, Header components
│   │   ├── Common/          # Reusable UI components (Card, Slider, Input, etc.)
│   │   ├── Module1/         # Country Intelligence Hub
│   │   ├── Module2/         # Visa & Documentation Tracker
│   │   ├── Module3/         # Financial Planning Module
│   │   ├── Module4/         # Job Market Intelligence
│   │   ├── Module5/         # Growth Forecast Module
│   │   └── Module6/         # Monthly Refresh Dashboard
│   ├── store/               # Zustand state management
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions (currency, calculations)
│   ├── services/            # API services (Anthropic)
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles with Tailwind directives
├── index.html               # HTML template
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── postcss.config.js        # PostCSS configuration
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Monthly Refresh Checklist

This application is designed for monthly refresh cycles. Each month, review and update:

- [ ] Policy changes in target countries
- [ ] New visa rules and requirements
- [ ] Salary market data updates
- [ ] AI re-analysis for updated outlooks
- [ ] Geopolitical updates
- [ ] Economic indicator adjustments
- [ ] Living standards index updates
- [ ] Progress on personal milestones

## Data Persistence

All user data is automatically saved to localStorage, including:
- Country profiles and indicators
- Visa pathway selections
- Financial planning inputs
- Document checklist status
- Personal milestones
- Settings and preferences

Export your data monthly as JSON backup using the export button in the header.

## API Integration

### Anthropic Claude API

The Growth Forecast Module uses Anthropic's Claude API for AI-powered country analysis. To enable:

1. Get an API key from [Anthropic](https://www.anthropic.com/)
2. Add it to your `.env` file: `VITE_ANTHROPIC_API_KEY=your_key`
3. Restart the development server

The app will use `claude-sonnet-4-6` model for generating country outlooks.

## Git Repository

This project is part of the MotasimAleem repository at `https://github.com/mohdmotasim/MotasimAleem`.

Location: `C:\Users\HP\OneDrive\Desktop\Bis\hijrah\`

### Commit Changes

```bash
cd C:\Users\HP\OneDrive\Desktop\Bis
git add hijrah/
git commit -m "Update Hijrah project"
git push
```

## Development Roadmap

- [x] Project scaffolding with TypeScript
- [x] State management with Zustand
- [x] Layout with sidebar navigation
- [x] Module 1: Country Intelligence Hub
- [ ] Module 2: Visa & Documentation Tracker
- [ ] Module 3: Financial Planning Module
- [ ] Module 4: Job Market Intelligence
- [ ] Module 5: Growth Forecast Module
- [ ] Module 6: Monthly Refresh Dashboard
- [ ] Settings panel with currency toggle
- [ ] Dark mode implementation
- [ ] Print/PDF export functionality

## License

This project is open source and available under the MIT License.
