import React from 'react';
import {
  Menu,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Clock,
  ExternalLink,
} from 'lucide-react';
import { SourceStatus } from '../../types/api';

interface TopNavProps {
  activeTab: string;
  sourceStatus: SourceStatus | null;
  onOpenMobileSidebar: () => void;
  onOpenStatusModal: () => void;
  onRefresh?: () => void;
}

const TAB_TITLES: Record<string, { title: string; subtitle: string }> = {
  'india-overview': {
    title: 'India National Overview',
    subtitle: 'National renewable generation, installed capacity, and technology mix',
  },
  'india-map': {
    title: 'Interactive India Map',
    subtitle: 'Geographic choropleth, regional grid overlays, and state-level telemetry',
  },
  'india-states': {
    title: 'State & UT Explorer',
    subtitle: 'Operational profiles across all 28 states and 8 union territories',
  },
  'india-regional': {
    title: 'Regional Grid Comparison',
    subtitle: 'NR, WR, SR, ER, and NER grid council metrics and interconnection flows',
  },
  'india-multi-year': {
    title: 'Multi-Year Analytics (2020–2026)',
    subtitle: 'Historical growth trajectory, annual additions, and compound growth rates',
  },
  'india-wind': {
    title: 'Wind Energy Sector Intelligence',
    subtitle: 'Onshore turbine fleet, seasonal monsoon surges, and non-wind state disclosures',
  },
  'india-solar': {
    title: 'Solar Photovoltaic Intelligence',
    subtitle: 'Utility-scale solar parks, spring outturn peaks, and solar radiation regimes',
  },
  'india-hydro': {
    title: 'Hydroelectric Energy Intelligence',
    subtitle: 'Large Hydro (>25MW), Small Hydro (<=25MW), and Himalayan river runoff',
  },
  'india-capacity': {
    title: 'Capacity & 500 GW Target Tracker',
    subtitle: 'Auditing progress toward India COP26 non-fossil capacity commitment',
  },
  'india-forecasting': {
    title: 'Forecasting & REMC Accuracy',
    subtitle: '96 intraday 15-minute time blocks, Day-Ahead schedules, and DSM errors',
  },
  'india-weather': {
    title: 'Renewable Weather Intelligence',
    subtitle: '100m hub-height wind velocity, Global Horizontal Irradiance, and monsoon index',
  },
  'india-explorer': {
    title: 'Data Explorer & Ledger',
    subtitle: '18,213 normalized observations, custom filtering, and CSV export',
  },
  'india-data-quality': {
    title: 'Data Quality & Provenance Audit',
    subtitle: 'Jurisdictional completeness matrix (36/36) and statutory ingestion audit trail',
  },
  'india-methodology': {
    title: 'Technical Methodology & Standards',
    subtitle: 'CEA statutory framework, CERC IEGC rules, unit standards, and error formulas',
  },
};

export const TopNav: React.FC<TopNavProps> = ({
  activeTab,
  sourceStatus,
  onOpenMobileSidebar,
  onOpenStatusModal,
  onRefresh,
}) => {
  const currentTabInfo = TAB_TITLES[activeTab] || TAB_TITLES['india-overview'];

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-nature-border">
      {/* Top Header Bar */}
      <div className="h-14 px-4 sm:px-6 flex items-center justify-between gap-4">
        {/* Left: Mobile Toggle & Page Title */}
        <div className="flex items-center space-x-3 truncate">
          <button
            onClick={onOpenMobileSidebar}
            className="lg:hidden p-1.5 rounded-md text-nature-muted hover:text-nature-text hover:bg-nature-bg transition-colors"
            title="Open Menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="truncate">
            <h1 className="text-sm sm:text-base font-semibold text-nature-text tracking-tight truncate">
              {currentTabInfo.title}
            </h1>
            <p className="hidden md:block text-[11px] text-nature-muted truncate">
              {currentTabInfo.subtitle}
            </p>
          </div>
        </div>

        {/* Right: Statutory Source & Live Status Indicator */}
        <div className="flex items-center space-x-2.5 flex-shrink-0">
          {/* Provenance Badge */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-nature-bg border border-nature-border text-xs text-nature-text">
            <span className="w-1.5 h-1.5 rounded-full bg-nature-actual" />
            <span className="font-mono text-[11px] text-nature-forest font-medium">
              CEA & Grid-India &bull; Verified + Reanalysis
            </span>
          </div>

          {/* Refresh Action */}
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-1.5 rounded-md text-nature-muted hover:text-nature-text hover:bg-nature-bg border border-transparent hover:border-nature-border transition-colors"
              title="Refresh Data"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Source Status Inspector Button */}
          <button
            onClick={onOpenStatusModal}
            className="flex items-center space-x-1 px-2.5 py-1 rounded-md bg-nature-forest-light text-nature-forest border border-nature-forest/20 text-xs font-medium hover:bg-nature-forest/15 transition-colors shadow-2xs"
            title="Inspect Platform Status & Provenance"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-nature-forest" />
            <span className="hidden sm:inline">Data Status</span>
          </button>
        </div>
      </div>
    </header>
  );
};
