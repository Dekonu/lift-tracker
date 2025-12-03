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
    <div className="min-h-screen bg-neutral-50">
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-neutral-900 mb-2">Dashboard</h1>
            <p className="text-neutral-600">Welcome back! Here's your workout overview.</p>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              {/* Quick Stats Cards */}
              <div className="card p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-neutral-600 mb-1">Workouts This Month</p>
                    <p className="text-3xl font-bold text-neutral-900">
                      {stats?.period_stats?.workout_count || 0}
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-lg bg-primary-100 flex items-center justify-center">
                    <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-neutral-600 mb-1">Volume This Month</p>
                    <p className="text-3xl font-bold text-neutral-900">
                      {stats?.period_stats?.total_volume_kg?.toLocaleString() || 0}
                      <span className="text-lg text-neutral-600 ml-1">kg</span>
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-lg bg-accent-100 flex items-center justify-center">
                    <svg className="h-6 w-6 text-accent-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-neutral-600 mb-1">Upcoming Workouts</p>
                    <p className="text-3xl font-bold text-neutral-900">
                      {stats?.upcoming?.scheduled_workouts_next_7_days || 0}
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-lg bg-primary-100 flex items-center justify-center">
                    <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-neutral-600 mb-1">Workouts/Week</p>
                    <p className="text-3xl font-bold text-neutral-900">
                      {stats?.period_stats?.workouts_per_week?.toFixed(1) || 0}
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-lg bg-accent-100 flex items-center justify-center">
                    <svg className="h-6 w-6 text-accent-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-neutral-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <Link
                href="/workouts/create"
                className="card p-6 group hover:border-primary-200 hover:shadow-medium"
              >
                <div className="flex items-center space-x-3 mb-3">
                  <div className="h-10 w-10 rounded-lg bg-primary-100 group-hover:bg-primary-200 flex items-center justify-center transition-colors">
                    <svg className="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </div>
                  <h4 className="text-lg font-semibold text-neutral-900">Start Workout</h4>
                </div>
                <p className="text-sm text-neutral-600">Create a new workout session</p>
              </Link>

              <Link
                href="/calendar"
                className="card p-6 group hover:border-primary-200 hover:shadow-medium"
              >
                <div className="flex items-center space-x-3 mb-3">
                  <div className="h-10 w-10 rounded-lg bg-accent-100 group-hover:bg-accent-200 flex items-center justify-center transition-colors">
                    <svg className="h-5 w-5 text-accent-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h4 className="text-lg font-semibold text-neutral-900">View Calendar</h4>
                </div>
                <p className="text-sm text-neutral-600">Schedule and view workouts</p>
              </Link>

              <Link
                href="/programs"
                className="card p-6 group hover:border-primary-200 hover:shadow-medium"
              >
                <div className="flex items-center space-x-3 mb-3">
                  <div className="h-10 w-10 rounded-lg bg-primary-100 group-hover:bg-primary-200 flex items-center justify-center transition-colors">
                    <svg className="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <h4 className="text-lg font-semibold text-neutral-900">Programs</h4>
                </div>
                <p className="text-sm text-neutral-600">Create and manage programs</p>
              </Link>
            </div>
          </div>

          {/* Today's Workout */}
          {stats?.today?.workout && (
            <div className="card p-6">
              <h3 className="text-xl font-semibold text-neutral-900 mb-4">Today's Workout</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-lg font-semibold text-neutral-900 mb-1">
                    {stats.today.workout.name || "Untitled Workout"}
                  </p>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      stats.today.workout.completed 
                        ? "bg-green-100 text-green-800" 
                        : "bg-primary-100 text-primary-800"
                    }`}>
                      {stats.today.workout.completed ? "Completed" : "In Progress"}
                    </span>
                  </div>
                </div>
                {!stats.today.workout.completed && (
                  <Link
                    href={`/workouts/${stats.today.workout.id}`}
                    className="btn-primary"
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

