import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ErrorAlert } from '../components/common/ErrorAlert';

describe('ErrorAlert Component', () => {
  it('renders error title, message, and executes retry callback', () => {
    const handleRetry = vi.fn();
    render(
      <ErrorAlert
        title="Network Timeout"
        message="Failed to connect to CEA generation endpoint"
        onRetry={handleRetry}
      />
    );

    expect(screen.getByText('Network Timeout')).toBeInTheDocument();
    expect(screen.getByText('Failed to connect to CEA generation endpoint')).toBeInTheDocument();

    const retryBtn = screen.getByText('Retry Request');
    fireEvent.click(retryBtn);

    expect(handleRetry).toHaveBeenCalledTimes(1);
  });
});

