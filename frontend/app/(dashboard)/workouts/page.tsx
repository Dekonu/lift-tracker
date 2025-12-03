"use client";

import { useState } from "react";
import { useWorkoutSessions, useDeleteWorkoutSession } from "@/lib/hooks/use-workouts";
import { format } from "date-fns";
import Link from "next/link";

export default function WorkoutsPage() {
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");
  const { data: workouts = [], isLoading } = useWorkoutSessions();
  const deleteWorkout = useDeleteWorkoutSession();

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this workout?")) {
      try {
        await deleteWorkout.mutateAsync(id);
      } catch (error) {
        console.error("Failed to delete workout:", error);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">Loading workouts...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Workouts</h2>
          <div className="flex items-center space-x-4">
            <div className="flex border border-gray-300 rounded-md">
              <button
                onClick={() => setViewMode("list")}
                className={`px-4 py-2 text-sm font-medium ${
                  viewMode === "list"
                    ? "bg-indigo-600 text-white"
                    : "bg-white text-gray-700 hover:bg-gray-50"
                }`}
              >
                List
              </button>
              <button
                onClick={() => setViewMode("grid")}
                className={`px-4 py-2 text-sm font-medium ${
                  viewMode === "grid"
                    ? "bg-indigo-600 text-white"
                    : "bg-white text-gray-700 hover:bg-gray-50"
                }`}
              >
                Grid
              </button>
            </div>
            <Link
              href="/workouts/create"
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Create Workout
            </Link>
          </div>
        </div>

        {workouts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No workouts yet.</p>
            <Link
              href="/workouts/create"
              className="text-indigo-600 hover:text-indigo-500 font-medium"
            >
              Create your first workout →
            </Link>
          </div>
        ) : viewMode === "list" ? (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {workouts.map((workout: any) => (
                <li key={workout.id}>
                  <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 flex items-center justify-center rounded-full bg-indigo-100">
                            <span className="text-indigo-600 font-medium">
                              {format(new Date(workout.started_at), "d")}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {workout.name || "Workout"}
                          </div>
                          <div className="text-sm text-gray-500">
                            {format(new Date(workout.started_at), "MMMM d, yyyy 'at' h:mm a")}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-sm text-gray-500">
                          {workout.total_volume_kg ? `${workout.total_volume_kg.toFixed(1)} kg` : "—"}
                        </div>
                        <div className="text-sm text-gray-500">
                          {workout.total_sets || 0} sets
                        </div>
                        <div className="flex space-x-2">
                          <Link
                            href={`/workouts/${workout.id}`}
                            className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                          >
                            View
                          </Link>
                          <button
                            onClick={() => handleDelete(workout.id)}
                            className="text-red-600 hover:text-red-500 text-sm font-medium"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {workouts.map((workout: any) => (
              <div
                key={workout.id}
                className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    {workout.name || "Workout"}
                  </h3>
                  <span className="text-sm text-gray-500">
                    {format(new Date(workout.started_at), "MMM d")}
                  </span>
                </div>
                <div className="space-y-2 mb-4">
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">Volume:</span>{" "}
                    <span className="text-gray-600">
                      {workout.total_volume_kg ? `${workout.total_volume_kg.toFixed(1)} kg` : "—"}
                    </span>
                  </div>
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">Sets:</span>{" "}
                    <span className="text-gray-600">{workout.total_sets || 0}</span>
                  </div>
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">Status:</span>{" "}
                    <span className="text-gray-600">
                      {workout.completed_at ? "Completed" : "In Progress"}
                    </span>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Link
                    href={`/workouts/${workout.id}`}
                    className="flex-1 text-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
                  >
                    View
                  </Link>
                  <button
                    onClick={() => handleDelete(workout.id)}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

