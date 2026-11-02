import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Sidebar } from '../components/layout/Sidebar';

describe('Sidebar Navigation Hierarchy', () => {
  it('renders all 14 India platform views across 5 statutory categories', () => {
    const handleSelectTab = vi.fn();
    const handleOpenStatus = vi.fn();

    render(
      <Sidebar
        activeTab="india-overview"
        onSelectTab={handleSelectTab}
        sourceStatus={null}
        onOpenStatusModal={handleOpenStatus}
      />
    );

    // Categories
    expect(screen.getByText('National Overview')).toBeInTheDocument();
    expect(screen.getByText('Geographic Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Technology Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Predictive & Weather')).toBeInTheDocument();
    expect(screen.getByText('Governance & Data')).toBeInTheDocument();

    // 14 India Views
    expect(screen.getByText('India Overview')).toBeInTheDocument();
    expect(screen.getByText('Interactive Map')).toBeInTheDocument();
    expect(screen.getByText('State & UT Explorer')).toBeInTheDocument();
    expect(screen.getByText('Regional Comparison')).toBeInTheDocument();
    expect(screen.getByText('Multi-Year Analytics')).toBeInTheDocument();
    expect(screen.getByText('Wind Energy')).toBeInTheDocument();
    expect(screen.getByText('Solar Energy')).toBeInTheDocument();
    expect(screen.getByText('Hydroelectric Energy')).toBeInTheDocument();
    expect(screen.getByText('Capacity & 500GW Target')).toBeInTheDocument();
    expect(screen.getByText('Forecasting & Accuracy')).toBeInTheDocument();
    expect(screen.getByText('Weather Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Data Explorer')).toBeInTheDocument();
    expect(screen.getByText('Quality & Provenance')).toBeInTheDocument();
    expect(screen.getByText('Methodology & Standards')).toBeInTheDocument();

    // Click tab
    fireEvent.click(screen.getByText('Regional Comparison'));
    expect(handleSelectTab).toHaveBeenCalledWith('india-regional');
  });
});

