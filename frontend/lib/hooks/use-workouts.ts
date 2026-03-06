"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

export function useWorkoutSessions(startDate?: Date, endDate?: Date) {
  const params = new URLSearchParams();
  if (startDate) params.append("start_date", startDate.toISOString());
  if (endDate) params.append("end_date", endDate.toISOString());

  return useQuery({
    queryKey: ["workout-sessions", startDate?.toISOString(), endDate?.toISOString()],
    queryFn: async () => {
      const response = await apiClient.get(
        `/workout-sessions?page=1&items_per_page=1000${params.toString() ? `&${params.toString()}` : ""}`
      );
      return response.data.data || [];
    },
  });
}

export function useWorkoutSession(id: number | null) {
  return useQuery({
    queryKey: ["workout-session", id],
    queryFn: async () => {
      if (!id) return null;
      const response = await apiClient.get(`/workout-session/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateWorkoutSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { started_at: string; name?: string | null }) => {
      const response = await apiClient.post("/workout-session", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workout-sessions"] });
    },
  });
}

export function useUpdateWorkoutSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: number;
      data: { started_at?: string; completed_at?: string; notes?: string };
    }) => {
      const response = await apiClient.patch(`/workout-session/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workout-sessions"] });
    },
  });
}

export function useDeleteWorkoutSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/workout-session/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workout-sessions"] });
    },
  });
}

