"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

export function usePrograms() {
  return useQuery({
    queryKey: ["programs"],
    queryFn: async () => {
      const response = await apiClient.get("/programs?page=1&items_per_page=100");
      return response.data.data || [];
    },
  });
}

export function useProgram(id: number | null) {
  return useQuery({
    queryKey: ["program", id],
    queryFn: async () => {
      if (!id) return null;
      const response = await apiClient.get(`/program/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateProgram() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      name: string;
      duration_weeks: number;
      days_per_week: number;
      periodization_type: string;
      description?: string;
    }) => {
      const response = await apiClient.post("/program", data);
      return response.data;
    },
    onSuccess: (data) => {
      // Immediately refetch programs to show the new program
      queryClient.refetchQueries({ queryKey: ["programs"] });
    },
  });
}

export function useWorkoutTemplates() {
  return useQuery({
    queryKey: ["workout-templates"],
    queryFn: async () => {
      const response = await apiClient.get("/workout-templates?page=1&items_per_page=100");
      return response.data.data || [];
    },
  });
}

export function useScheduleProgram() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      programId: number;
      startDate: string;
    }) => {
      // The endpoint expects start_date as a query parameter
      // Format: ISO 8601 datetime string
      const response = await apiClient.post(
        `/program/${data.programId}/schedule`,
        null,
        {
          params: {
            start_date: data.startDate,
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["programs"] });
      queryClient.invalidateQueries({ queryKey: ["scheduled-workouts"] });
    },
  });
}

