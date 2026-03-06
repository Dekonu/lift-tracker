"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

export function useEquipment() {
  return useQuery({
    queryKey: ["equipment"],
    queryFn: async () => {
      const response = await apiClient.get("/equipment?page=1&items_per_page=1000&enabled=true");
      return response.data.data || [];
    },
    staleTime: 60 * 60 * 1000, // 1 hour - equipment doesn't change often
  });
}

