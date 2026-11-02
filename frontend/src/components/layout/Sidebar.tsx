import React from 'react';
import {
  Wind,
  LayoutDashboard,
  Map,
  MapPin,
  Layers,
  TrendingUp,
  Sun,
  Droplets,
  Target,
  LineChart,
  CloudSun,
  Database,
  ShieldCheck,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Award,
} from 'lucide-react';
import { SourceStatus } from '../../types/api';

interface SidebarProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
  sourceStatus: SourceStatus | null;
  onOpenStatusModal: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  isMobileOpen?: boolean;
  onCloseMobile?: () => void;
}

interface NavCategory {
  title: string;
  items: {
    id: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
  }[];
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  sourceStatus,
  onOpenStatusModal,
  isCollapsed = false,
  onToggleCollapse,
  isMobileOpen = false,
  onCloseMobile,
}) => {
  const NAV_CATEGORIES: NavCategory[] = [
    {
      title: 'National Overview',
      items: [
        { id: 'india-overview', label: 'India Overview', icon: LayoutDashboard },
        { id: 'india-map', label: 'Interactive Map', icon: Map },
      ],
    },
    {
      title: 'Geographic Intelligence',
      items: [
        { id: 'india-states', label: 'State & UT Explorer', icon: MapPin },
        { id: 'india-regional', label: 'Regional Comparison', icon: Layers },
        { id: 'india-multi-year', label: 'Multi-Year Analytics', icon: TrendingUp },
      ],
    },
    {
      title: 'Technology Intelligence',
      items: [
        { id: 'india-wind', label: 'Wind Energy', icon: Wind },
        { id: 'india-solar', label: 'Solar Energy', icon: Sun },
        { id: 'india-hydro', label: 'Hydroelectric Energy', icon: Droplets },
        { id: 'india-capacity', label: 'Capacity & 500GW Target', icon: Target },
      ],
    },
    {
      title: 'Predictive & Weather',
      items: [
        { id: 'india-forecasting', label: 'Forecasting & Accuracy', icon: LineChart },
        { id: 'india-weather', label: 'Weather Intelligence', icon: CloudSun },
      ],
    },
    {
      title: 'Governance & Data',
      items: [
        { id: 'india-explorer', label: 'Data Explorer', icon: Database },
        { id: 'india-data-quality', label: 'Quality & Provenance', icon: ShieldCheck },
        { id: 'india-methodology', label: 'Methodology & Standards', icon: BookOpen },
      ],
    },
  ];

  const handleNavClick = (tabId: string) => {
    onSelectTab(tabId);
    if (onCloseMobile) onCloseMobile();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-[#26332C]/40 backdrop-blur-sm lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 flex flex-col bg-white border-r border-nature-border transition-all duration-200 ease-in-out ${
          isMobileOpen
            ? 'translate-x-0 w-64'
            : '-translate-x-full lg:translate-x-0'
        } ${isCollapsed ? 'lg:w-16' : 'lg:w-64'}`}
      >
        {/* Brand Header */}
        <div className="h-14 flex items-center justify-between px-3.5 border-b border-nature-border bg-white flex-shrink-0">
          <div className="flex items-center space-x-2.5 overflow-hidden">
            <div className="flex-shrink-0 w-8 h-8 rounded-md bg-nature-forest-light border border-nature-border flex items-center justify-center text-nature-forest">
              <Wind className="w-4 h-4" />
            </div>
            {!isCollapsed && (
              <div className="truncate">
                <div className="flex items-center space-x-1.5">
                  <span className="font-semibold text-sm text-nature-text tracking-tight">
                    WindScope
                  </span>
                  <span className="font-bold text-xs text-nature-forest font-mono bg-emerald-50 px-1 py-0.2 rounded border border-emerald-200">
                    INDIA
                  </span>
                </div>
                <p className="text-[10px] text-nature-muted truncate font-medium">
                  Powered by CEA & Grid-India Data
                </p>
              </div>
            )}
          </div>

          {onToggleCollapse && (
            <button
              onClick={onToggleCollapse}
              className="hidden lg:flex items-center justify-center w-6 h-6 rounded text-nature-muted hover:text-nature-text hover:bg-nature-bg transition-colors"
              title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            >
              {isCollapsed ? (
                <ChevronRight className="w-3.5 h-3.5" />
              ) : (
                <ChevronLeft className="w-3.5 h-3.5" />
              )}
            </button>
          )}
        </div>

        {/* Navigation Categories */}
        <nav className="flex-1 py-2 px-2 space-y-3 overflow-y-auto">
          {NAV_CATEGORIES.map((category) => (
            <div key={category.title} className="space-y-0.5">
              {!isCollapsed && (
                <div className="px-2.5 pt-1.5 pb-1 text-[10px] font-bold uppercase tracking-wider text-nature-muted/70">
                  {category.title}
                </div>
              )}
              {category.items.map((item) => {
                const isActive = activeTab === item.id;
                const Icon = item.icon;

                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavClick(item.id)}
                    className={`w-full flex items-center rounded-md py-1.5 text-xs transition-colors ${
                      isActive
                        ? 'bg-nature-forest-light text-nature-forest font-semibold border-l-2 border-nature-forest pl-2.5 pr-2'
                        : 'text-nature-muted hover:text-nature-text hover:bg-nature-bg pl-3 pr-2'
                    } ${isCollapsed ? 'justify-center px-0' : 'justify-start'}`}
                    title={item.label}
                  >
                    <Icon
                      className={`w-4 h-4 flex-shrink-0 ${
                        isActive ? 'text-nature-forest' : 'text-nature-muted'
                      } ${!isCollapsed ? 'mr-2.5' : ''}`}
                    />
                    {!isCollapsed && <span className="truncate">{item.label}</span>}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Telemetry Status Footer */}
        <div className="p-2.5 border-t border-nature-border bg-[#FAFCF9] flex-shrink-0">
          <button
            onClick={onOpenStatusModal}
            className="w-full flex items-center justify-between p-2 rounded-md bg-white hover:bg-nature-bg border border-nature-border text-[11px] text-nature-text transition-colors shadow-xs"
            title="Inspect Platform Status & Data Provenance"
          >
            <div className="flex items-center space-x-2 truncate">
              <span className="w-2 h-2 rounded-full flex-shrink-0 bg-nature-actual" />
              {!isCollapsed && (
                <span className="truncate text-nature-text font-medium">
                  Statutory Pipeline Active
                </span>
              )}
            </div>
            {!isCollapsed && (
              <span className="text-[10px] text-nature-muted font-mono">&rarr;</span>
            )}
          </button>
        </div>
      </aside>
    </>
  );
};
