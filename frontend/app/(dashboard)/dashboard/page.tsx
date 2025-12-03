"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";

export default function DashboardPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  // Redirect if not authenticated
  useEffect(() => {
    if (user === null && typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (!token) {
        router.push("/login");
      }
    }
  }, [user, router]);

  // Fetch dashboard stats
  const { data: stats, isLoading } = useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: async () => {
      const response = await apiClient.get("/dashboard/stats?period=month");
      return response.data;
    },
    enabled: !!user,
  });

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Lift Tracker</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user.name}</span>
              <button
                onClick={() => {
                  localStorage.removeItem("access_token");
                  router.push("/login");
                }}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h2>

          {isLoading ? (
            <div>Loading stats...</div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {/* Quick Stats Cards */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl font-bold text-gray-900">
                        {stats?.period_stats?.workout_count || 0}
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Workouts This Month
                        </dt>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl font-bold text-gray-900">
                        {stats?.period_stats?.total_volume_kg?.toLocaleString() || 0} kg
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Volume This Month
                        </dt>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl font-bold text-gray-900">
                        {stats?.upcoming?.scheduled_workouts_next_7_days || 0}
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Upcoming Workouts
                        </dt>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl font-bold text-gray-900">
                        {stats?.period_stats?.workouts_per_week?.toFixed(1) || 0}
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Workouts/Week
                        </dt>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="mt-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <Link
                href="/workouts/create"
                className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
              >
                <h4 className="text-lg font-medium text-gray-900">Start Workout</h4>
                <p className="text-sm text-gray-500 mt-2">Create a new workout session</p>
              </Link>

              <Link
                href="/calendar"
                className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
              >
                <h4 className="text-lg font-medium text-gray-900">View Calendar</h4>
                <p className="text-sm text-gray-500 mt-2">Schedule and view workouts</p>
              </Link>

              <Link
                href="/programs"
                className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
              >
                <h4 className="text-lg font-medium text-gray-900">Programs</h4>
                <p className="text-sm text-gray-500 mt-2">Create and manage programs</p>
              </Link>
            </div>
          </div>

          {/* Today's Workout */}
          {stats?.today?.workout && (
            <div className="mt-8 bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Today's Workout</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {stats.today.workout.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {stats.today.workout.completed ? "Completed" : "In Progress"}
                  </p>
                </div>
                {!stats.today.workout.completed && (
                  <Link
                    href={`/workouts/${stats.today.workout.id}`}
                    className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                  >
                    Continue →
                  </Link>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

