"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

export function useScheduledWorkouts(startDate?: Date, endDate?: Date) {
  const params = new URLSearchParams();
  if (startDate) params.append("start_date", startDate.toISOString());
  if (endDate) params.append("end_date", endDate.toISOString());

  return useQuery({
    queryKey: ["scheduled-workouts", startDate?.toISOString(), endDate?.toISOString()],
    queryFn: async () => {
      const response = await apiClient.get(
        `/scheduled-workouts?${params.toString()}`
      );
      return response.data.data || [];
    },
  });
}

export function useCreateScheduledWorkout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      scheduled_date: string;
      workout_template_id: number;
      program_id?: number;
      program_week?: number;
      notes?: string;
    }) => {
      const response = await apiClient.post("/scheduled-workout", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduled-workouts"] });
    },
  });
}

export function useUpdateScheduledWorkout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: number;
      data: {
        scheduled_date?: string;
        status?: string;
        notes?: string;
        completed_workout_session_id?: number;
      };
    }) => {
      const response = await apiClient.patch(`/scheduled-workout/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduled-workouts"] });
    },
  });
}

export function useDeleteScheduledWorkout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/scheduled-workout/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduled-workouts"] });
    },
  });
}

export function useScheduleProgram() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      programId,
      startDate,
    }: {
      programId: number;
      startDate: string;
    }) => {
      const response = await apiClient.post(
        `/program/${programId}/schedule?start_date=${startDate}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduled-workouts"] });
      queryClient.invalidateQueries({ queryKey: ["programs"] });
    },
  });
}

