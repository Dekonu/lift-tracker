"use client";

import { useRequireAuth } from "@/lib/hooks/use-auth";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLogout } from "@/lib/stores/auth-store";

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
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link href="/dashboard" className="text-xl font-bold text-gray-900">
                  Lift Tracker
                </Link>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navigation.map((item) => {
                  const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                        isActive
                          ? "border-indigo-500 text-gray-900"
                          : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                      }`}
                    >
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700 text-sm">Welcome, {user.name}</span>
              <button
                onClick={logout}
                className="text-gray-600 hover:text-gray-900 text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main>{children}</main>
    </div>
  );
}

