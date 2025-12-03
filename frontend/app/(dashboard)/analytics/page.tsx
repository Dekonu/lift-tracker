"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<"week" | "month" | "year" | "all">("month");

  const { data: dashboardStats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard", "stats", period],
    queryFn: async () => {
      const response = await apiClient.get(`/dashboard/stats?period=${period}`);
      return response.data;
    },
  });

  const { data: volumeData, isLoading: volumeLoading } = useQuery({
    queryKey: ["analytics", "volume"],
    queryFn: async () => {
      const response = await apiClient.get("/analytics/volume?page=1&items_per_page=100");
      return response.data.data || [];
    },
  });

  // Transform volume data for chart
  const volumeChartData = volumeData?.map((item: any) => ({
    date: new Date(item.period_start).toLocaleDateString(),
    volume: item.total_volume_kg || 0,
  })) || [];

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value as any)}
            className="border border-gray-300 rounded-md px-4 py-2"
          >
            <option value="week">Week</option>
            <option value="month">Month</option>
            <option value="year">Year</option>
            <option value="all">All Time</option>
          </select>
        </div>

        {statsLoading ? (
          <div>Loading analytics...</div>
        ) : (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="text-sm font-medium text-gray-500">Total Volume</div>
                <div className="text-2xl font-bold text-gray-900 mt-2">
                  {dashboardStats?.period_stats?.total_volume_kg?.toLocaleString() || 0} kg
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="text-sm font-medium text-gray-500">Workouts</div>
                <div className="text-2xl font-bold text-gray-900 mt-2">
                  {dashboardStats?.period_stats?.workout_count || 0}
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="text-sm font-medium text-gray-500">Workouts/Week</div>
                <div className="text-2xl font-bold text-gray-900 mt-2">
                  {dashboardStats?.period_stats?.workouts_per_week?.toFixed(1) || 0}
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="text-sm font-medium text-gray-500">Total Sets</div>
                <div className="text-2xl font-bold text-gray-900 mt-2">
                  {dashboardStats?.period_stats?.total_sets || 0}
                </div>
              </div>
            </div>

            {/* Volume Trend Chart */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Volume Trend</h3>
              {volumeLoading ? (
                <div>Loading chart data...</div>
              ) : volumeChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={volumeChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="volume" stroke="#4F46E5" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  No volume data available. Complete some workouts to see trends.
                </div>
              )}
            </div>

            {/* All-Time Stats */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">All-Time Statistics</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-500">Total Volume (All Time)</div>
                  <div className="text-xl font-bold text-gray-900 mt-1">
                    {dashboardStats?.all_time_stats?.total_volume_kg?.toLocaleString() || 0} kg
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Total Workouts (All Time)</div>
                  <div className="text-xl font-bold text-gray-900 mt-1">
                    {dashboardStats?.all_time_stats?.total_workouts || 0}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

