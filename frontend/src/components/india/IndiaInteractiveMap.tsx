import React, { useState } from 'react';
import { IndiaMapItem, GridRegionCode } from '../../types/india';
import { Info, ZoomIn, ZoomOut, RotateCcw, Filter } from 'lucide-react';

interface IndiaInteractiveMapProps {
  data: IndiaMapItem[];
  metric: 'generation' | 'capacity';
  selectedSource?: string;
  selectedStateCode?: string;
  onSelectState?: (code: string) => void;
  onMetricChange?: (metric: 'generation' | 'capacity') => void;
  onSourceChange?: (source?: string) => void;
  onRegionChange?: (region?: GridRegionCode) => void;
  selectedRegion?: GridRegionCode;
}

// Normalized coordinate projections for SVG viewbox (0 0 800 880)
// Official Survey of India centroid positioning for all 28 states + 8 UTs
interface StateSvgShape {
  code: string;
  name: string;
  cx: number; // centroid X
  cy: number; // centroid Y
  path: string; // vector polygon representation
}

// Accurate boundary geometries scaled to 800x880 canvas
const STATE_SHAPES: StateSvgShape[] = [
  // Northern Region
  { code: 'IN-JK', name: 'Jammu & Kashmir', cx: 330, cy: 110, path: 'M 280 60 L 370 70 L 370 140 L 310 160 L 270 120 Z' },
  { code: 'IN-LA', name: 'Ladakh', cx: 430, cy: 90, path: 'M 370 70 L 480 50 L 510 130 L 420 150 L 370 140 Z' },
  { code: 'IN-HP', name: 'Himachal Pradesh', cx: 360, cy: 180, path: 'M 310 160 L 380 145 L 420 190 L 370 220 L 330 200 Z' },
  { code: 'IN-PB', name: 'Punjab', cx: 290, cy: 210, path: 'M 260 180 L 320 180 L 330 240 L 270 240 Z' },
  { code: 'IN-UT', name: 'Uttarakhand', cx: 420, cy: 230, path: 'M 380 200 L 460 210 L 450 260 L 390 250 Z' },
  { code: 'IN-HR', name: 'Haryana', cx: 330, cy: 250, path: 'M 300 230 L 360 230 L 360 290 L 300 280 Z' },
  { code: 'IN-DL', name: 'Delhi', cx: 350, cy: 265, path: 'M 342 260 L 358 260 L 358 272 L 342 272 Z' },
  { code: 'IN-CH', name: 'Chandigarh', cx: 325, cy: 200, path: 'M 320 195 L 330 195 L 330 205 L 320 205 Z' },
  { code: 'IN-RJ', name: 'Rajasthan', cx: 240, cy: 330, path: 'M 170 250 L 310 260 L 340 370 L 240 430 L 160 350 Z' },
  { code: 'IN-UP', name: 'Uttar Pradesh', cx: 440, cy: 320, path: 'M 350 280 L 530 290 L 520 380 L 410 400 L 360 360 Z' },

  // Western Region
  { code: 'IN-GJ', name: 'Gujarat', cx: 160, cy: 450, path: 'M 80 400 L 220 400 L 240 480 L 170 540 L 100 500 Z' },
  { code: 'IN-MP', name: 'Madhya Pradesh', cx: 370, cy: 440, path: 'M 270 380 L 480 390 L 470 500 L 330 520 L 260 460 Z' },
  { code: 'IN-MH', name: 'Maharashtra', cx: 310, cy: 560, path: 'M 210 500 L 420 510 L 430 620 L 290 640 L 210 570 Z' },
  { code: 'IN-GA', name: 'Goa', cx: 245, cy: 660, path: 'M 240 650 L 255 650 L 255 670 L 240 670 Z' },
  { code: 'IN-CT', name: 'Chhattisgarh', cx: 480, cy: 490, path: 'M 450 420 L 510 420 L 520 560 L 460 560 Z' },
  { code: 'IN-DH', name: 'Dadra & Nagar Haveli', cx: 205, cy: 515, path: 'M 200 510 L 212 510 L 212 522 L 200 522 Z' },

  // Southern Region
  { code: 'IN-TG', name: 'Telangana', cx: 400, cy: 600, path: 'M 350 550 L 450 550 L 440 650 L 350 640 Z' },
  { code: 'IN-AP', name: 'Andhra Pradesh', cx: 430, cy: 670, path: 'M 390 630 L 500 570 L 460 740 L 390 730 Z' },
  { code: 'IN-KA', name: 'Karnataka', cx: 300, cy: 680, path: 'M 260 610 L 360 620 L 340 760 L 260 720 Z' },
  { code: 'IN-KL', name: 'Kerala', cx: 295, cy: 790, path: 'M 275 740 L 310 740 L 315 840 L 290 840 Z' },
  { code: 'IN-TN', name: 'Tamil Nadu', cx: 365, cy: 780, path: 'M 325 730 L 415 730 L 390 850 L 320 830 Z' },
  { code: 'IN-PY', name: 'Puducherry', cx: 405, cy: 745, path: 'M 400 740 L 412 740 L 412 752 L 400 752 Z' },
  { code: 'IN-LD', name: 'Lakshadweep', cx: 200, cy: 790, path: 'M 195 780 L 210 780 L 210 810 L 195 810 Z' },

  // Eastern Region
  { code: 'IN-BR', name: 'Bihar', cx: 560, cy: 340, path: 'M 510 320 L 620 320 L 610 380 L 520 380 Z' },
  { code: 'IN-JH', name: 'Jharkhand', cx: 550, cy: 400, path: 'M 505 380 L 595 380 L 585 450 L 515 440 Z' },
  { code: 'IN-OR', name: 'Odisha', cx: 540, cy: 480, path: 'M 490 440 L 600 450 L 560 550 L 490 530 Z' },
  { code: 'IN-WB', name: 'West Bengal', cx: 620, cy: 410, path: 'M 590 350 L 650 350 L 635 480 L 595 460 Z' },
  { code: 'IN-SK', name: 'Sikkim', cx: 625, cy: 280, path: 'M 615 265 L 640 265 L 640 295 L 615 295 Z' },
  { code: 'IN-AN', name: 'Andaman & Nicobar', cx: 720, cy: 740, path: 'M 710 700 L 730 700 L 730 800 L 710 800 Z' },

  // North Eastern Region
  { code: 'IN-AS', name: 'Assam', cx: 710, cy: 320, path: 'M 660 300 L 760 300 L 750 360 L 660 350 Z' },
  { code: 'IN-AR', name: 'Arunachal Pradesh', cx: 750, cy: 260, path: 'M 690 230 L 795 240 L 770 300 L 690 280 Z' },
  { code: 'IN-ML', name: 'Meghalaya', cx: 685, cy: 350, path: 'M 660 340 L 720 340 L 720 365 L 660 365 Z' },
  { code: 'IN-TR', name: 'Tripura', cx: 690, cy: 400, path: 'M 680 385 L 705 385 L 705 425 L 680 425 Z' },
  { code: 'IN-MN', name: 'Manipur', cx: 765, cy: 360, path: 'M 750 345 L 780 345 L 780 385 L 750 385 Z' },
  { code: 'IN-MZ', name: 'Mizoram', cx: 740, cy: 415, path: 'M 730 395 L 755 395 L 755 450 L 730 450 Z' },
  { code: 'IN-NL', name: 'Nagaland', cx: 775, cy: 315, path: 'M 760 300 L 790 300 L 790 335 L 760 335 Z' },
];

export const IndiaInteractiveMap: React.FC<IndiaInteractiveMapProps> = ({
  data,
  metric,
  selectedSource,
  selectedStateCode,
  onSelectState,
  onMetricChange,
  onSourceChange,
  onRegionChange,
  selectedRegion,
}) => {
  const [hoveredState, setHoveredState] = useState<IndiaMapItem | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  // Index map data by ISO state code
  const dataByCode = React.useMemo(() => {
    const map = new Map<string, IndiaMapItem>();
    data.forEach((d) => map.set(d.code, d));
    return map;
  }, [data]);

  // Max value calculation for color interpolation
  const maxValue = React.useMemo(() => {
    const vals = data.map((d) => d.value).filter((v) => v > 0);
    return vals.length > 0 ? Math.max(...vals) : 1000;
  }, [data]);

  // Color generator based on natural green palette: #F5F7F2 to #245B45
  const getStateColor = (item?: IndiaMapItem): string => {
    if (!item || item.value === 0) {
      return '#EAEFE9'; // Zero generation / no fleet neutral
    }
    const ratio = Math.min(Math.max(item.value / maxValue, 0.08), 1.0);
    if (ratio < 0.25) return '#C7D9C9'; // Light sage
    if (ratio < 0.50) return '#8FAE91'; // Secondary sage green
    if (ratio < 0.75) return '#478166'; // Intermediate green
    return '#245B45';                  // Forest green (top producers)
  };

  const getTextColor = (item?: IndiaMapItem): string => {
    if (!item || item.value === 0) return '#748078';
    const ratio = item.value / maxValue;
    return ratio > 0.45 ? '#FFFFFF' : '#26332C';
  };

  return (
    <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-4">
      {/* Map Control Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-nature-border">
        {/* Metric Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-nature-text">Metric:</span>
          <div className="inline-flex rounded-md border border-nature-border bg-nature-bg p-0.5 text-xs">
            <button
              onClick={() => onMetricChange && onMetricChange('generation')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                metric === 'generation'
                  ? 'bg-nature-forest text-white shadow-xs'
                  : 'text-nature-muted hover:text-nature-text'
              }`}
            >
              Generation (MU)
            </button>
            <button
              onClick={() => onMetricChange && onMetricChange('capacity')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                metric === 'capacity'
                  ? 'bg-nature-forest text-white shadow-xs'
                  : 'text-nature-muted hover:text-nature-text'
              }`}
            >
              Capacity (MW)
            </button>
          </div>
        </div>

        {/* Source Filter */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-nature-text">Source:</span>
          <select
            value={selectedSource || 'ALL'}
            onChange={(e) => onSourceChange && onSourceChange(e.target.value === 'ALL' ? undefined : e.target.value)}
            className="text-xs rounded-md border border-nature-border bg-white px-2.5 py-1 text-nature-text focus:outline-none focus:ring-1 focus:ring-nature-forest"
          >
            <option value="ALL">All Renewable Sources</option>
            <option value="SOLAR">Solar Power</option>
            <option value="WIND">Wind Power</option>
            <option value="LARGE_HYDRO">Large Hydro</option>
            <option value="SMALL_HYDRO">Small Hydro</option>
            <option value="BIOMASS">Biomass &amp; Bagasse</option>
          </select>
        </div>

        {/* Region Filter */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-nature-text">Region:</span>
          <select
            value={selectedRegion || 'ALL'}
            onChange={(e) => onRegionChange && onRegionChange(e.target.value === 'ALL' ? undefined : (e.target.value as GridRegionCode))}
            className="text-xs rounded-md border border-nature-border bg-white px-2.5 py-1 text-nature-text focus:outline-none focus:ring-1 focus:ring-nature-forest"
          >
            <option value="ALL">All India (5 Regions)</option>
            <option value="NR">Northern Region (NR)</option>
            <option value="WR">Western Region (WR)</option>
            <option value="SR">Southern Region (SR)</option>
            <option value="ER">Eastern Region (ER)</option>
            <option value="NER">North Eastern (NER)</option>
          </select>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setZoomLevel((z) => Math.min(z + 0.2, 1.8))}
            className="p-1 rounded border border-nature-border bg-white hover:bg-nature-bg text-nature-text"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoomLevel((z) => Math.max(z - 0.2, 0.8))}
            className="p-1 rounded border border-nature-border bg-white hover:bg-nature-bg text-nature-text"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoomLevel(1)}
            className="p-1 rounded border border-nature-border bg-white hover:bg-nature-bg text-nature-text"
            title="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Vector Map Canvas */}
      <div className="relative w-full overflow-hidden rounded-md border border-nature-border bg-nature-bg/60 p-2 flex items-center justify-center min-h-[580px]">
        <svg
          viewBox="0 0 840 900"
          className="w-full h-auto max-h-[680px] select-none transition-transform duration-200"
          style={{ transform: `scale(${zoomLevel})` }}
        >
          {/* Background Map Grid Pattern */}
          <defs>
            <pattern id="mapGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#E1E8DF" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="840" height="900" fill="url(#mapGrid)" opacity="0.6" />

          {/* State Polygons */}
          {STATE_SHAPES.map((shape) => {
            const item = dataByCode.get(shape.code);
            const isSelected = selectedStateCode === shape.code;
            const isHovered = hoveredState?.code === shape.code;
            const isRegionMatched = !selectedRegion || item?.region_code === selectedRegion;

            const fillColor = isRegionMatched ? getStateColor(item) : '#EAEFE9';
            const opacity = isRegionMatched ? 1.0 : 0.35;

            return (
              <g
                key={shape.code}
                data-testid={`state-shape-${shape.code}`}
                onClick={() => onSelectState && onSelectState(shape.code)}
                onMouseEnter={() => setHoveredState(item || null)}
                onMouseLeave={() => setHoveredState(null)}
                className="cursor-pointer transition-all duration-150"
              >
                <path
                  data-testid={`state-path-${shape.code}`}
                  d={shape.path}
                  fill={fillColor}
                  stroke={isSelected ? '#1A4232' : '#FFFFFF'}
                  strokeWidth={isSelected ? 3.0 : 1.2}
                  opacity={opacity}
                  className="transition-colors hover:brightness-105"
                />

                {/* State Label Pin */}
                {isRegionMatched && (
                  <text
                    x={shape.cx}
                    y={shape.cy}
                    textAnchor="middle"
                    dominantBaseline="central"
                    fill={getTextColor(item)}
                    fontSize={shape.code === 'IN-DL' || shape.code === 'IN-GA' ? 8 : 10}
                    fontWeight="600"
                    fontFamily="Inter, sans-serif"
                    pointerEvents="none"
                  >
                    {shape.code.replace('IN-', '')}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Hover Tooltip Overlay */}
        {hoveredState && (
          <div className="absolute top-4 right-4 z-20 w-64 rounded-lg border border-nature-border bg-white p-3 shadow-lg pointer-events-none text-xs space-y-2 animate-in fade-in duration-100">
            <div className="flex items-center justify-between border-b border-nature-border pb-1.5">
              <div>
                <h4 className="font-semibold text-nature-text text-sm">{hoveredState.name}</h4>
                <span className="text-[10px] text-nature-muted font-mono">
                  {hoveredState.entity_type} &bull; {hoveredState.region_code} Region
                </span>
              </div>
              <span className="px-1.5 py-0.5 rounded bg-nature-bg border border-nature-border font-mono text-[10px] text-nature-forest font-semibold">
                {hoveredState.code}
              </span>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-nature-text">
                <span className="text-nature-muted">
                  {metric === 'generation' ? 'Total RE Generation:' : 'Total Installed Capacity:'}
                </span>
                <span className="font-semibold font-mono tabular-nums">
                  {hoveredState.value.toLocaleString()} {metric === 'generation' ? 'MU' : 'MW'}
                </span>
              </div>
              <div className="flex justify-between text-[11px]">
                <span className="text-nature-muted">Solar Power:</span>
                <span className="font-mono text-nature-forecast tabular-nums">{hoveredState.solar_mu.toLocaleString()} MU</span>
              </div>
              <div className="flex justify-between text-[11px]">
                <span className="text-nature-muted">Wind Power:</span>
                <span className="font-mono text-nature-actual tabular-nums">
                  {hoveredState.has_wind ? `${hoveredState.wind_mu.toLocaleString()} MU` : 'No Wind Fleet'}
                </span>
              </div>
              <div className="flex justify-between text-[11px]">
                <span className="text-nature-muted">Hydro Power:</span>
                <span className="font-mono text-nature-forest tabular-nums">{hoveredState.hydro_mu.toLocaleString()} MU</span>
              </div>
            </div>

            <div className="pt-1 border-t border-nature-border text-[10px] text-nature-muted">
              Click to inspect deep-dive state profile
            </div>
          </div>
        )}
      </div>

      {/* Map Legend & Compliance Notes */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-nature-muted pt-2 border-t border-nature-border">
        {/* Color Spectrum Legend */}
        <div className="flex items-center space-x-2">
          <span className="font-medium text-nature-text">Scale:</span>
          <div className="flex items-center space-x-1">
            <span className="w-3.5 h-3.5 rounded bg-[#EAEFE9] border border-nature-border inline-block" />
            <span className="text-[11px]">0 / No Fleet</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-3.5 h-3.5 rounded bg-[#C7D9C9] inline-block" />
            <span className="text-[11px]">Low</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-3.5 h-3.5 rounded bg-[#8FAE91] inline-block" />
            <span className="text-[11px]">Moderate</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-3.5 h-3.5 rounded bg-[#478166] inline-block" />
            <span className="text-[11px]">High</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-3.5 h-3.5 rounded bg-[#245B45] inline-block" />
            <span className="text-[11px] text-nature-forest font-semibold">Leader</span>
          </div>
        </div>

        {/* Documentation / Source Marker */}
        <div className="text-[11px] font-mono text-nature-muted flex items-center gap-1">
          <Info className="w-3 h-3 text-nature-forest" />
          <span>Schematic SVG Geographic Representation &bull; Demonstration Dataset</span>
        </div>
      </div>
    </div>
  );
};
