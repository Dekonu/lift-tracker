import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useWorkoutSessions } from '@/lib/hooks/use-workouts';
import { apiClient } from '@/lib/api/client';

vi.mock('@/lib/api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe('useWorkoutSessions', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('fetches workout sessions successfully', async () => {
    const mockWorkouts = [
      { id: 1, name: 'Push Day', started_at: '2024-01-01' },
      { id: 2, name: 'Pull Day', started_at: '2024-01-02' },
    ];

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { data: mockWorkouts, total_count: 2, has_more: false },
    } as any);

    const { result } = renderHook(() => useWorkoutSessions(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockWorkouts);
  });

  it('handles API errors gracefully', async () => {
    vi.mocked(apiClient.get).mockRejectedValue(new Error('API Error'));

    const { result } = renderHook(() => useWorkoutSessions(), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});

