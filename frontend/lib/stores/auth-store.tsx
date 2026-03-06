"use client";

import { create } from "zustand";
import { apiClient } from "@/lib/api/client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

interface User {
  id: number;
  name: string;
  email: string;
  is_superuser?: boolean;
}

interface AuthState {
  user: User | null;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}));

// Auth provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { setUser } = useAuthStore();
  const queryClient = useQueryClient();

  // Check if user is logged in on mount
  useQuery({
    queryKey: ["user", "me"],
    queryFn: async () => {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setUser(null);
        return null;
      }

      try {
        const response = await apiClient.get("/user/me/");
        const userData = response.data;
        setUser({
          ...userData,
          is_superuser: userData.is_superuser || false,
        });
        return userData;
      } catch (error) {
        localStorage.removeItem("access_token");
        setUser(null);
        return null;
      }
    },
    retry: false,
  });

  return <>{children}</>;
}

// Login mutation
export function useLogin() {
  const { setUser } = useAuthStore();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      email,
      password,
    }: {
      email: string;
      password: string;
    }) => {
      const params = new URLSearchParams();
      params.append("username", email);
      params.append("password", password);

      const response = await apiClient.post("/login", params.toString(), {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const { access_token } = response.data;
      localStorage.setItem("access_token", access_token);

      // Fetch user data
      const userResponse = await apiClient.get("/user/me/");
      const userData = userResponse.data;
      setUser({
        ...userData,
        is_superuser: userData.is_superuser || false,
      });

      return userData;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user", "me"] });
    },
  });
}

// Logout function
export function useLogout() {
  const { setUser } = useAuthStore();
  const queryClient = useQueryClient();

  return () => {
    localStorage.removeItem("access_token");
    setUser(null);
    queryClient.clear();
  };
}

