import React from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  X,
  ExternalLink,
  Cpu,
  Database,
  Radio,
  Clock,
  Zap,
} from 'lucide-react';
import { SourceStatus } from '../../types/api';

interface SystemStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  status: SourceStatus | null;
  onRefresh?: () => void;
}

export const SystemStatusModal: React.FC<SystemStatusModalProps> = ({
  isOpen,
  onClose,
  status,
  onRefresh,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-in fade-in duration-150">
      <div
        className="w-full max-w-xl rounded-lg border border-nature-border bg-white shadow-2xl overflow-hidden text-nature-text"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-4 py-3 border-b border-nature-border flex items-center justify-between bg-nature-bg">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-nature-forest" />
            <h3 className="text-xs font-semibold text-nature-text uppercase tracking-wider font-sans">
              India Renewable Energy Pipeline &amp; System Status
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-nature-muted hover:text-nature-text hover:bg-nature-border/50 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-3.5 max-h-[75vh] overflow-y-auto font-mono text-xs">
          {/* Main Status Banner */}
          <div className="p-3 rounded-md border flex items-start space-x-2.5 bg-emerald-50 border-emerald-200 text-emerald-950">
            <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
            <div className="space-y-1 font-sans">
              <div className="font-semibold text-xs">
                Official Statutory Pipeline &bull; Operational
              </div>
              <p className="text-[11px] text-nature-text leading-relaxed">
                Integrated with Central Electricity Authority (CEA), Grid Controller of India Limited (NLDC), and National Power Portal (NPP).
              </p>
            </div>
          </div>

          {/* Service Streams Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {/* CEA Stream */}
            <div className="p-3 rounded-md bg-nature-bg border border-nature-border space-y-1.5">
              <div className="flex items-center justify-between font-sans">
                <span className="font-semibold text-nature-text flex items-center gap-1.5 text-xs">
                  <Database className="w-3.5 h-3.5 text-nature-forest" /> CEA Monthly OPM
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 inline-flex items-center gap-1 font-mono">
                  <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" /> ACTIVE
                </span>
              </div>
              <div className="text-[11px] text-nature-muted space-y-0.5 font-sans">
                <div className="flex justify-between">
                  <span>Scope:</span> <strong className="text-nature-text">28 States &amp; 8 UTs</strong>
                </div>
                <div className="flex justify-between">
                  <span>Fuels:</span> <span className="text-nature-text font-mono">Wind, Solar, Hydro</span>
                </div>
                <div className="flex justify-between">
                  <span>Provenance:</span> <span>Section 73(i) EA 2003</span>
                </div>
              </div>
            </div>

            {/* Grid-India NLDC Stream */}
            <div className="p-3 rounded-md bg-nature-bg border border-nature-border space-y-1.5">
              <div className="flex items-center justify-between font-sans">
                <span className="font-semibold text-nature-text flex items-center gap-1.5 text-xs">
                  <Radio className="w-3.5 h-3.5 text-nature-actual" /> Grid-India NLDC
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 inline-flex items-center gap-1 font-mono">
                  <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" /> ACTIVE
                </span>
              </div>
              <div className="text-[11px] text-nature-muted space-y-0.5 font-sans">
                <div className="flex justify-between">
                  <span>Report:</span> <strong className="text-nature-text">Daily PSP &amp; Telemetry</strong>
                </div>
                <div className="flex justify-between">
                  <span>Accounting:</span> <span className="text-nature-text font-mono">4 Measures (CERC)</span>
                </div>
                <div className="flex justify-between">
                  <span>Cadence:</span> <span>Daily / 15-min blocks</span>
                </div>
              </div>
            </div>
          </div>

          {/* Scope Parameters */}
          <div className="p-3.5 rounded-md bg-nature-bg border border-nature-border space-y-2">
            <h4 className="font-sans font-medium text-nature-text text-xs flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-nature-forest" /> Regulatory &amp; Technical Specifications
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[11px]">
              <div className="p-2 rounded bg-white border border-nature-border">
                <span className="block text-nature-muted text-[10px] font-sans">Jurisdiction</span>
                <strong className="text-nature-text">India (All 36 States/UTs)</strong>
              </div>
              <div className="p-2 rounded bg-white border border-nature-border">
                <span className="block text-nature-muted text-[10px] font-sans">Grid Timezone</span>
                <strong className="text-nature-text">Asia/Kolkata (IST, UTC+5:30)</strong>
              </div>
              <div className="p-2 rounded bg-white border border-nature-border">
                <span className="block text-nature-muted text-[10px] font-sans">Block Resolution</span>
                <strong className="text-nature-text">15-Minute (96 Blocks/Day)</strong>
              </div>
              <div className="p-2 rounded bg-white border border-nature-border">
                <span className="block text-nature-muted text-[10px] font-sans">DAM / GDAM Cutoff</span>
                <strong className="text-nature-text">12:00 PM IST (Day D-1)</strong>
              </div>
              <div className="p-2 rounded bg-white border border-nature-border">
                <span className="block text-nature-muted text-[10px] font-sans">RTM Gate Closure</span>
                <strong className="text-nature-text">T - 75 Mins (CERC IEGC)</strong>
              </div>
              <div className="p-2 rounded bg-white border border-nature-border">
                <span className="block text-nature-muted text-[10px] font-sans">Primary Authority</span>
                <strong className="text-nature-text">CEA, Grid-India, CERC</strong>
              </div>
            </div>
          </div>

          {/* External Statutory Links */}
          <div className="pt-1 flex flex-wrap items-center justify-between gap-2 text-nature-muted text-[11px] font-sans">
            <div className="flex items-center space-x-3">
              <a
                href="https://cea.nic.in"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-nature-forest flex items-center gap-1 underline underline-offset-4"
              >
                <span>CEA Portal</span>
                <ExternalLink className="w-3 h-3" />
              </a>
              <a
                href="https://grid-india.in"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-nature-forest flex items-center gap-1 underline underline-offset-4"
              >
                <span>Grid-India NLDC</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="px-2 py-0.5 rounded bg-white hover:bg-nature-bg text-nature-text border border-nature-border text-xs shadow-xs"
              >
                Refresh Pipeline Status
              </button>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-nature-border bg-nature-bg flex justify-end">
          <button
            onClick={onClose}
            className="px-3.5 py-1 rounded bg-white hover:bg-nature-border/30 text-nature-text border border-nature-border font-medium text-xs font-sans transition-colors shadow-sm"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
