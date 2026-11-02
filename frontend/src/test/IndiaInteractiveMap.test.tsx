import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { IndiaInteractiveMap } from '../components/india/IndiaInteractiveMap';
import { IndiaMapItem } from '../types/india';

const mockMapData: IndiaMapItem[] = [
  {
    code: 'IN-GJ',
    name: 'Gujarat',
    entity_type: 'STATE',
    region_code: 'WR',
    geojson_id: 'IN-GJ',
    latitude: 22.2587,
    longitude: 71.1924,
    total_generation_mu: 12500,
    total_capacity_mw: 24000,
    solar_mu: 5500,
    wind_mu: 6000,
    hydro_mu: 800,
    biomass_mu: 200,
    other_mu: 0,
    solar_capacity_mw: 13000,
    wind_capacity_mw: 10500,
    has_wind: true,
    value: 12500,
  },
  {
    code: 'IN-TN',
    name: 'Tamil Nadu',
    entity_type: 'STATE',
    region_code: 'SR',
    geojson_id: 'IN-TN',
    latitude: 11.1271,
    longitude: 78.6569,
    total_generation_mu: 11800,
    total_capacity_mw: 21500,
    solar_mu: 4800,
    wind_mu: 6200,
    hydro_mu: 600,
    biomass_mu: 200,
    other_mu: 0,
    solar_capacity_mw: 9500,
    wind_capacity_mw: 10800,
    has_wind: true,
    value: 11800,
  },
  {
    code: 'IN-BR',
    name: 'Bihar',
    entity_type: 'STATE',
    region_code: 'ER',
    geojson_id: 'IN-BR',
    latitude: 25.0961,
    longitude: 85.3131,
    total_generation_mu: 350,
    total_capacity_mw: 600,
    solar_mu: 280,
    wind_mu: 0,
    hydro_mu: 50,
    biomass_mu: 20,
    other_mu: 0,
    solar_capacity_mw: 500,
    wind_capacity_mw: 0,
    has_wind: false,
    value: 350,
  },
];

describe('IndiaInteractiveMap Component', () => {
  it('renders interactive map container, metric controls, and state shapes', () => {
    const handleSelect = vi.fn();
    render(
      <IndiaInteractiveMap
        data={mockMapData}
        metric="generation"
        selectedStateCode="IN-GJ"
        onSelectState={handleSelect}
      />
    );

    // Metric toggle buttons
    expect(screen.getByText('Generation (MU)')).toBeInTheDocument();
    expect(screen.getByText('Capacity (MW)')).toBeInTheDocument();

    // Region dropdown
    expect(screen.getByText('All India (5 Regions)')).toBeInTheDocument();
    expect(screen.getByText('Southern Region (SR)')).toBeInTheDocument();

    // Legend
    expect(screen.getByText('Scale:')).toBeInTheDocument();
    expect(screen.getByText('Leader')).toBeInTheDocument();

    // Click on Gujarat shape
    const gjShape = screen.getByTestId('state-shape-IN-GJ');
    expect(gjShape).toBeInTheDocument();
    fireEvent.click(gjShape);
    expect(handleSelect).toHaveBeenCalledWith('IN-GJ');
  });

  it('filters by region when selectedRegion prop is provided', () => {
    render(
      <IndiaInteractiveMap
        data={mockMapData}
        metric="generation"
        selectedRegion="SR"
      />
    );

    // Tamil Nadu shape (SR) should have full opacity, Gujarat shape (WR) dimmed
    const tnPath = screen.getByTestId('state-path-IN-TN');
    const gjPath = screen.getByTestId('state-path-IN-GJ');
    expect(tnPath).toHaveAttribute('opacity', '1');
    expect(gjPath).toHaveAttribute('opacity', '0.35');
  });
});
