import { redirect } from "next/navigation";
import { useAuthStore } from "@/lib/stores/auth-store";

export default function Home() {
  // This will be handled client-side
  return redirect("/dashboard");
}

