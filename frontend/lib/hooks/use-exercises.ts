"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

export function useExercises() {
  return useQuery({
    queryKey: ["exercises"],
    queryFn: async () => {
      const response = await apiClient.get("/exercises?page=1&items_per_page=1000");
      return response.data.data || [];
    },
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

