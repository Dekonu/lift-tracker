"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useExercises } from "@/lib/hooks/use-exercises";

export default function ProgressPage() {
  const [timePeriod, setTimePeriod] = useState<"week" | "month" | "year" | "all">("month");
  const { data: exercises = [] } = useExercises();

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard-stats", timePeriod],
    queryFn: async () => {
      const response = await apiClient.get(`/dashboard/stats?period=${timePeriod}`);
      return response.data;
    },
  });

  // Fetch workout sessions for volume chart
  const { data: sessionsData, isLoading: sessionsLoading } = useQuery({
    queryKey: ["workout-sessions", timePeriod],
    queryFn: async () => {
      const response = await apiClient.get("/workout-sessions?page=1&items_per_page=100");
      return response.data.data || [];
    },
  });

  // Fetch strength progression
  const { data: strengthData, isLoading: strengthLoading } = useQuery({
    queryKey: ["strength-progression", timePeriod],
    queryFn: async () => {
      const response = await apiClient.get(`/analytics/strength-progression?page=1&items_per_page=50`);
      return response.data.data || [];
    },
  });

  // Process volume data for chart
  const volumeChartData = sessionsData
    ?.filter((s: any) => s.completed_at && s.total_volume_kg)
    .map((s: any) => ({
      date: new Date(s.started_at).toLocaleDateString(),
      volume: s.total_volume_kg || 0,
      sets: s.total_sets || 0,
    }))
    .sort((a: any, b: any) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(-30) || []; // Last 30 workouts

  // Process strength progression by exercise
  const strengthByExercise: Record<string, any[]> = {};
  strengthData?.forEach((entry: any) => {
    const exercise = exercises.find((e: any) => e.id === entry.exercise_id);
    const exerciseName = exercise?.name || `Exercise ${entry.exercise_id}`;
    if (!strengthByExercise[exerciseName]) {
      strengthByExercise[exerciseName] = [];
    }
    strengthByExercise[exerciseName].push({
      date: new Date(entry.date).toLocaleDateString(),
      maxWeight: entry.max_weight_kg || 0,
      estimated1RM: entry.estimated_1rm || 0,
    });
  });

  if (statsLoading || sessionsLoading || strengthLoading) {
    return (
      <div className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
      <div className="px-4 sm:px-0">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <h1 className="text-3xl font-bold text-neutral-900">Progress Dashboard</h1>
            <select
              value={timePeriod}
              onChange={(e) => setTimePeriod(e.target.value as any)}
              className="border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="year">Last Year</option>
              <option value="all">All Time</option>
            </select>
          </div>
          <p className="text-neutral-600">Track your training progress and performance metrics.</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card p-6">
            <div className="text-sm font-medium text-neutral-700 mb-1">Total Volume</div>
            <div className="text-3xl font-bold text-neutral-900">
              {stats?.total_volume_kg
                ? `${(stats.total_volume_kg / 1000).toFixed(1)}k kg`
                : "0 kg"}
            </div>
            <div className="text-xs text-neutral-500 mt-1">
              {stats?.all_time_volume_kg
                ? `${(stats.all_time_volume_kg / 1000).toFixed(1)}k kg all time`
                : ""}
            </div>
          </div>

          <div className="card p-6">
            <div className="text-sm font-medium text-neutral-700 mb-1">Workouts Completed</div>
            <div className="text-3xl font-bold text-neutral-900">
              {stats?.workout_count || 0}
            </div>
            <div className="text-xs text-neutral-500 mt-1">
              {stats?.all_time_workouts || 0} all time
            </div>
          </div>

          <div className="card p-6">
            <div className="text-sm font-medium text-neutral-700 mb-1">Total Sets</div>
            <div className="text-3xl font-bold text-neutral-900">
              {stats?.total_sets || 0}
            </div>
            <div className="text-xs text-neutral-500 mt-1">Completed sets</div>
          </div>

          <div className="card p-6">
            <div className="text-sm font-medium text-neutral-700 mb-1">Training Frequency</div>
            <div className="text-3xl font-bold text-neutral-900">
              {stats?.workout_count
                ? (stats.workout_count / (timePeriod === "week" ? 1 : timePeriod === "month" ? 4 : timePeriod === "year" ? 52 : 1)).toFixed(1)
                : "0"}
            </div>
            <div className="text-xs text-neutral-500 mt-1">workouts per week</div>
          </div>
        </div>

        {/* Volume Trend Chart */}
        <div className="card p-6 mb-8">
          <h2 className="text-xl font-semibold text-neutral-900 mb-4">Volume Trend</h2>
          {volumeChartData.length > 0 ? (
            <div className="h-64 flex items-end justify-between gap-1">
              {volumeChartData.map((data: any, idx: number) => {
                const maxVolume = Math.max(...volumeChartData.map((d: any) => d.volume));
                const height = maxVolume > 0 ? (data.volume / maxVolume) * 100 : 0;
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-primary-600 rounded-t hover:bg-primary-700 transition-colors"
                      style={{ height: `${Math.max(height, 5)}%` }}
                      title={`${data.date}: ${data.volume.toFixed(0)} kg`}
                    />
                    {idx % 5 === 0 && (
                      <span className="text-xs text-neutral-500 mt-1 transform -rotate-45 origin-top-left">
                        {data.date.split("/")[0]}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
            <div className="mt-4 text-sm text-neutral-600">
              Showing last {volumeChartData.length} workouts
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-neutral-500">
              No workout data available for this period
            </div>
          )}
        </div>

        {/* Strength Progression */}
        {Object.keys(strengthByExercise).length > 0 && (
          <div className="card p-6 mb-8">
            <h2 className="text-xl font-semibold text-neutral-900 mb-4">Strength Progression</h2>
            <div className="space-y-6">
              {Object.entries(strengthByExercise)
                .slice(0, 5) // Show top 5 exercises
                .map(([exerciseName, data]) => {
                  const maxWeight = Math.max(...data.map((d: any) => d.maxWeight));
                  const minWeight = Math.min(...data.map((d: any) => d.maxWeight));
                  const range = maxWeight - minWeight || 1;

                  return (
                    <div key={exerciseName}>
                      <div className="flex justify-between items-center mb-2">
                        <h3 className="font-medium text-neutral-900">{exerciseName}</h3>
                        <span className="text-sm text-neutral-600">
                          Max: {maxWeight.toFixed(1)} kg
                        </span>
                      </div>
                      <div className="h-32 flex items-end justify-between gap-1">
                        {data.map((point: any, idx: number) => {
                          const height = ((point.maxWeight - minWeight) / range) * 100;
                          return (
                            <div key={idx} className="flex-1 flex flex-col items-center">
                              <div
                                className="w-full bg-green-600 rounded-t hover:bg-green-700 transition-colors"
                                style={{ height: `${Math.max(height, 5)}%` }}
                                title={`${point.date}: ${point.maxWeight.toFixed(1)} kg`}
                              />
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {/* Recent Workouts */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-neutral-900 mb-4">Recent Workouts</h2>
          {sessionsData && sessionsData.length > 0 ? (
            <div className="space-y-3">
              {sessionsData.slice(0, 10).map((session: any) => (
                <div
                  key={session.id}
                  className="border border-neutral-200 rounded-lg p-4 hover:bg-neutral-50 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-neutral-900">{session.name || "Workout"}</h3>
                      <p className="text-sm text-neutral-600 mt-1">
                        {new Date(session.started_at).toLocaleDateString()} at{" "}
                        {new Date(session.started_at).toLocaleTimeString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-neutral-900">
                        {session.total_volume_kg
                          ? `${(session.total_volume_kg / 1000).toFixed(1)}k kg`
                          : "0 kg"}
                      </div>
                      <div className="text-xs text-neutral-600">
                        {session.total_sets || 0} sets
                      </div>
                      {session.duration_minutes && (
                        <div className="text-xs text-neutral-600">
                          {session.duration_minutes} min
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-neutral-500 text-center py-8">
              No workouts found for this period
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

