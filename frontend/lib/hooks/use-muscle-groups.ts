"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

export function useMuscleGroups() {
  return useQuery({
    queryKey: ["muscle-groups"],
    queryFn: async () => {
      const response = await apiClient.get("/muscle-groups?page=1&items_per_page=1000");
      return response.data.data || [];
    },
    staleTime: 60 * 60 * 1000, // 1 hour - muscle groups don't change often
  });
}

