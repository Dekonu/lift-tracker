"use client";

import { useAuthStore } from "@/lib/stores/auth-store";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export function useRequireAuth() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();

  useEffect(() => {
    if (user === null && typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (!token) {
        router.push("/login");
      }
    }
  }, [user, router]);

  return user;
}

