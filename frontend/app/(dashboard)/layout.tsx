"use client";

import { useRequireAuth } from "@/lib/hooks/use-auth";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLogout } from "@/lib/stores/auth-store";
import Image from "next/image";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = useRequireAuth();
  const pathname = usePathname();
  const logout = useLogout();

  if (!user) {
    return null; // Will redirect in useRequireAuth
  }

  const navigation = [
    { name: "Dashboard", href: "/dashboard" },
    { name: "Calendar", href: "/calendar" },
    { name: "Programs", href: "/programs" },
    { name: "Workouts", href: "/workouts" },
    { name: "Analytics", href: "/analytics" },
    { name: "Exercises", href: "/exercises" },
  ];

  return (
    <div className="min-h-screen bg-neutral-50">
      <nav className="bg-white border-b border-neutral-200 sticky top-0 z-50 backdrop-blur-sm bg-white/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link href="/dashboard" className="flex items-center space-x-3 group">
                <div className="relative w-8 h-8">
                  <Image
                    src="/images/logo.png"
                    alt="Lift Tracker"
                    fill
                    className="object-contain group-hover:scale-105 transition-transform duration-200"
                    priority
                  />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
                  Lift Tracker
                </span>
              </Link>
              <div className="hidden md:flex md:space-x-1">
                {navigation.map((item) => {
                  const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={`nav-link ${
                        isActive
                          ? "active"
                          : "text-neutral-600 hover:text-neutral-900"
                      }`}
                    >
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="hidden sm:flex items-center space-x-3">
                <Link
                  href="/profile"
                  className="h-8 w-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-semibold text-sm hover:scale-105 transition-transform duration-200 cursor-pointer"
                >
                  {user.name?.charAt(0).toUpperCase() || "U"}
                </Link>
                <span className="text-neutral-700 text-sm font-medium">Welcome, {user.name}</span>
              </div>
              <button
                onClick={logout}
                className="text-neutral-600 hover:text-neutral-900 text-sm font-medium px-3 py-2 rounded-lg hover:bg-neutral-100 transition-colors duration-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="min-h-[calc(100vh-4rem)]">{children}</main>
    </div>
  );
}

