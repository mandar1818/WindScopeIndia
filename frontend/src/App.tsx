import React, { useState, useEffect, Suspense, lazy } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { TopNav } from './components/layout/TopNav';
import { SystemStatusModal } from './components/layout/SystemStatusModal';

// India Platform Pages (Dynamic Lazy-Loaded Chunks for Optimal Route Splitting)
const IndiaOverviewPage = lazy(() => import('./pages/india/IndiaOverviewPage').then(m => ({ default: m.IndiaOverviewPage })));
const IndiaMapPage = lazy(() => import('./pages/india/IndiaMapPage').then(m => ({ default: m.IndiaMapPage })));
const StateExplorerPage = lazy(() => import('./pages/india/StateExplorerPage').then(m => ({ default: m.StateExplorerPage })));
const RegionalComparisonPage = lazy(() => import('./pages/india/RegionalComparisonPage').then(m => ({ default: m.RegionalComparisonPage })));
const MultiYearAnalyticsPage = lazy(() => import('./pages/india/MultiYearAnalyticsPage').then(m => ({ default: m.MultiYearAnalyticsPage })));
const WindAnalyticsPage = lazy(() => import('./pages/india/WindAnalyticsPage').then(m => ({ default: m.WindAnalyticsPage })));
const SolarAnalyticsPage = lazy(() => import('./pages/india/SolarAnalyticsPage').then(m => ({ default: m.SolarAnalyticsPage })));
const HydroAnalyticsPage = lazy(() => import('./pages/india/HydroAnalyticsPage').then(m => ({ default: m.HydroAnalyticsPage })));
const CapacityTrackerPage = lazy(() => import('./pages/india/CapacityTrackerPage').then(m => ({ default: m.CapacityTrackerPage })));
const IndiaForecastingPage = lazy(() => import('./pages/india/IndiaForecastingPage').then(m => ({ default: m.IndiaForecastingPage })));
const WeatherIntelligencePage = lazy(() => import('./pages/india/WeatherIntelligencePage').then(m => ({ default: m.WeatherIntelligencePage })));
const IndiaDataExplorerPage = lazy(() => import('./pages/india/IndiaDataExplorerPage').then(m => ({ default: m.IndiaDataExplorerPage })));
const DataQualityPage = lazy(() => import('./pages/india/DataQualityPage').then(m => ({ default: m.DataQualityPage })));
const IndiaMethodologyPage = lazy(() => import('./pages/india/IndiaMethodologyPage').then(m => ({ default: m.IndiaMethodologyPage })));

import { indiaApi } from './services/indiaApi';
import { SourceStatus } from './types/api';

function PageLoadingSkeleton() {
  return (
    <div className="space-y-4 py-4 animate-pulse">
      <div className="h-10 bg-nature-border/40 rounded-lg w-1/3"></div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="h-24 bg-nature-border/30 rounded-lg"></div>
        <div className="h-24 bg-nature-border/30 rounded-lg"></div>
        <div className="h-24 bg-nature-border/30 rounded-lg"></div>
        <div className="h-24 bg-nature-border/30 rounded-lg"></div>
      </div>
      <div className="h-80 bg-nature-border/20 rounded-lg"></div>
    </div>
  );
}

export function App() {
  const [activeTab, setActiveTab] = useState<string>('india-overview');
  const [sourceStatus, setSourceStatus] = useState<SourceStatus | null>(null);
  const [isStatusModalOpen, setIsStatusModalOpen] = useState<boolean>(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);

  const fetchSourceStatus = async () => {
    try {
      const res = await indiaApi.getHealth();
      setSourceStatus({
        cea_api_online: true,
        grid_india_available: true,
        is_operational: true,
        data_source_description: 'Central Electricity Authority (CEA) & Grid-India NLDC Live Feeds',
        last_updated_utc: res.timestamp_utc,
      });
    } catch (e) {
      console.warn('Backend health status query failed:', e);
    }
  };

  useEffect(() => {
    fetchSourceStatus();
  }, []);

  return (
    <div className="min-h-screen bg-nature-bg text-nature-text flex flex-col font-sans selection:bg-nature-forest/15 selection:text-nature-forest">
      {/* Platform Shell */}
      <div className="flex flex-1">
        {/* Left Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          sourceStatus={sourceStatus}
          onOpenStatusModal={() => setIsStatusModalOpen(true)}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          isMobileOpen={isMobileSidebarOpen}
          onCloseMobile={() => setIsMobileSidebarOpen(false)}
        />

        {/* Right Main Application Area */}
        <div
          className={`flex-1 flex flex-col min-w-0 transition-all duration-200 ${
            isSidebarCollapsed ? 'lg:pl-16' : 'lg:pl-64'
          }`}
        >
          {/* Top Navigation Bar */}
          <TopNav
            activeTab={activeTab}
            sourceStatus={sourceStatus}
            onOpenMobileSidebar={() => setIsMobileSidebarOpen(true)}
            onOpenStatusModal={() => setIsStatusModalOpen(true)}
            onRefresh={fetchSourceStatus}
          />

          {/* Main Dashboard Pages Container */}
          <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
            <Suspense fallback={<PageLoadingSkeleton />}>
              {/* View 1: India Overview */}
              {activeTab === 'india-overview' && (
                <IndiaOverviewPage onNavigate={setActiveTab} />
              )}

              {/* View 2: Interactive India Map */}
              {activeTab === 'india-map' && <IndiaMapPage />}

              {/* View 3: State & UT Explorer */}
              {activeTab === 'india-states' && <StateExplorerPage />}

              {/* View 4: Regional Grid Comparison */}
              {activeTab === 'india-regional' && <RegionalComparisonPage />}

              {/* View 5: Multi-Year Analytics */}
              {activeTab === 'india-multi-year' && <MultiYearAnalyticsPage />}

              {/* View 6: Wind Energy Analytics */}
              {activeTab === 'india-wind' && <WindAnalyticsPage />}

              {/* View 7: Solar Energy Analytics */}
              {activeTab === 'india-solar' && <SolarAnalyticsPage />}

              {/* View 8: Hydro Energy Analytics */}
              {activeTab === 'india-hydro' && <HydroAnalyticsPage />}

              {/* View 9: Capacity & Target Tracker */}
              {activeTab === 'india-capacity' && <CapacityTrackerPage />}

              {/* View 10: Forecasting & Accuracy */}
              {activeTab === 'india-forecasting' && <IndiaForecastingPage />}

              {/* View 11: Weather Intelligence */}
              {activeTab === 'india-weather' && <WeatherIntelligencePage />}

              {/* View 12: Data Explorer */}
              {activeTab === 'india-explorer' && <IndiaDataExplorerPage />}

              {/* View 13: Data Quality & Provenance */}
              {activeTab === 'india-data-quality' && <DataQualityPage />}

              {/* View 14: Technical Methodology */}
              {activeTab === 'india-methodology' && <IndiaMethodologyPage />}
            </Suspense>
          </main>

          {/* Clean Natural Footer */}
          <footer className="border-t border-nature-border bg-white py-4 text-xs text-nature-muted mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex flex-wrap items-center space-x-2 text-[11px]">
                <span className="font-semibold text-nature-text">WindScope India</span>
                <span className="text-nature-border">&bull;</span>
                <span>Renewable Energy Intelligence Platform</span>
                <span className="text-nature-border">&bull;</span>
                <span className="font-mono text-nature-forest font-medium">28 States &amp; 8 Union Territories</span>
              </div>

              <div className="text-[11px] text-nature-muted font-mono text-center sm:text-right">
                Central Electricity Authority (CEA) &bull; National Power Portal (NPP) &bull; ISTS Grid
              </div>
            </div>
          </footer>
        </div>
      </div>

      {/* System Status Inspector Modal */}
      <SystemStatusModal
        isOpen={isStatusModalOpen}
        onClose={() => setIsStatusModalOpen(false)}
        status={sourceStatus}
        onRefresh={fetchSourceStatus}
      />
    </div>
  );
}
export default App;
