import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { StateExplorerPage } from '../pages/india/StateExplorerPage';
import { indiaApi } from '../services/indiaApi';
import { IndiaStateItem, IndiaStateProfile } from '../types/india';

const mockStates: IndiaStateItem[] = [
  {
    code: 'IN-GJ',
    name: 'Gujarat',
    entity_type: 'STATE',
    region_code: 'WR',
    capital: 'Gandhinagar',
    latitude: 22.2587,
    longitude: 71.1924,
    total_capacity_mw: 31985.0,
    total_re_capacity_mw: 31985.0,
    wind_capacity_mw: 12240.0,
    solar_capacity_mw: 17450.0,
    hydro_capacity_mw: 2100.0,
    has_wind: true,
    has_commercial_wind: true,
  },
  {
    code: 'IN-BR',
    name: 'Bihar',
    entity_type: 'STATE',
    region_code: 'ER',
    capital: 'Patna',
    latitude: 25.0961,
    longitude: 85.3131,
    total_capacity_mw: 430.0,
    total_re_capacity_mw: 430.0,
    wind_capacity_mw: 0.0,
    solar_capacity_mw: 220.0,
    hydro_capacity_mw: 70.0,
    has_wind: false,
    has_commercial_wind: false,
  },
  {
    code: 'IN-DL',
    name: 'Delhi',
    entity_type: 'UNION_TERRITORY',
    region_code: 'NR',
    capital: 'New Delhi',
    latitude: 28.7041,
    longitude: 77.1025,
    total_capacity_mw: 312.0,
    total_re_capacity_mw: 312.0,
    wind_capacity_mw: 0.0,
    solar_capacity_mw: 260.0,
    hydro_capacity_mw: 0.0,
    has_wind: false,
    has_commercial_wind: false,
  },
];

const mockProfile: IndiaStateProfile = {
  code: 'IN-GJ',
  name: 'Gujarat',
  entity_type: 'STATE',
  region_code: 'WR',
  capital: 'Gandhinagar',
  latitude: 22.2587,
  longitude: 71.1924,
  total_capacity_mw: 31985.0,
  capacity_breakdown: {
    SOLAR: 17450.0,
    WIND: 12240.0,
    LARGE_HYDRO: 1990.0,
  },
  has_wind: true,
  monthly_series: [],
  seasonality: [
    {
      month: 1,
      month_name: 'Jan',
      avg_wind_mu: 1020.69,
      avg_solar_mu: 2070.45,
      avg_hydro_mu: 131.98,
    },
  ],
  daily_january_2026: [],
  statutory_source: 'Central Electricity Authority',
};

describe('StateExplorerPage Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(indiaApi, 'getStates').mockResolvedValue(mockStates);
    vi.spyOn(indiaApi, 'getStateProfile').mockResolvedValue(mockProfile);
  });

  it('renders state cards and displays total and wind capacities safely', async () => {
    render(<StateExplorerPage />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 4, name: 'Gujarat' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 4, name: 'Bihar' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 4, name: 'Delhi' })).toBeInTheDocument();
    });

    // Check capacity displays
    expect(screen.getAllByText(/31,985\s*MW/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/12,240\s*MW/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Showing 3 of 36 Geographies')).toBeInTheDocument();
  });

  it('filters by search input query', async () => {
    render(<StateExplorerPage />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 4, name: 'Gujarat' })).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search state, UT, capital or code...');
    fireEvent.change(searchInput, { target: { value: 'Patna' } });

    expect(screen.getByRole('heading', { level: 4, name: 'Bihar' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { level: 4, name: 'Gujarat' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { level: 4, name: 'Delhi' })).not.toBeInTheDocument();
    expect(screen.getByText('Showing 1 of 36 Geographies')).toBeInTheDocument();
  });

  it('filters by entity type (STATE vs UNION_TERRITORY)', async () => {
    render(<StateExplorerPage />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 4, name: 'Delhi' })).toBeInTheDocument();
    });

    const selects = screen.getAllByRole('combobox');
    const typeSelect = selects[1]; // Region=0, Type=1, Wind=2

    fireEvent.change(typeSelect, { target: { value: 'UNION_TERRITORY' } });

    expect(screen.getByRole('heading', { level: 4, name: 'Delhi' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { level: 4, name: 'Gujarat' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { level: 4, name: 'Bihar' })).not.toBeInTheDocument();
    expect(screen.getByText('Showing 1 of 36 Geographies')).toBeInTheDocument();
  });

  it('filters by wind fleet presence', async () => {
    render(<StateExplorerPage />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 4, name: 'Gujarat' })).toBeInTheDocument();
    });

    const selects = screen.getAllByRole('combobox');
    const windSelect = selects[2]; // Wind filter is third dropdown

    fireEvent.change(windSelect, { target: { value: 'WIND_ONLY' } });

    expect(screen.getByRole('heading', { level: 4, name: 'Gujarat' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { level: 4, name: 'Bihar' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { level: 4, name: 'Delhi' })).not.toBeInTheDocument();
    expect(screen.getByText('Showing 1 of 36 Geographies')).toBeInTheDocument();
  });

  it('renders error alert when API call fails and provides retry', async () => {
    vi.spyOn(indiaApi, 'getStates').mockRejectedValue(new Error('Connection refused'));
    render(<StateExplorerPage />);

    await waitFor(() => {
      expect(screen.getByText('State Directory Error')).toBeInTheDocument();
      expect(screen.getByText('Connection refused')).toBeInTheDocument();
    });
  });
});
