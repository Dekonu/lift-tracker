"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useWorkoutSession, useUpdateWorkoutSession } from "@/lib/hooks/use-workouts";
import { useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { format } from "date-fns";

export default function WorkoutExecutionPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const workoutId = parseInt(params.id as string);
  const { data: workout, isLoading } = useWorkoutSession(workoutId);
  const updateWorkout = useUpdateWorkoutSession();
  const [restTimer, setRestTimer] = useState<number | null>(null);
  const [timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (timerInterval) {
      return () => clearInterval(timerInterval);
    }
  }, [timerInterval]);

  const startRestTimer = (seconds: number) => {
    if (timerInterval) {
      clearInterval(timerInterval);
    }
    setRestTimer(seconds);
    const interval = setInterval(() => {
      setRestTimer((prev) => {
        if (prev === null || prev <= 1) {
          clearInterval(interval);
          return null;
        }
        return prev - 1;
      });
    }, 1000);
    setTimerInterval(interval);
  };

  const stopRestTimer = () => {
    if (timerInterval) {
      clearInterval(timerInterval);
      setTimerInterval(null);
    }
    setRestTimer(null);
  };

  const handleCompleteWorkout = async () => {
    if (!workout) return;
    try {
      await updateWorkout.mutateAsync({
        id: workoutId,
        data: {
          completed_at: new Date().toISOString(),
        },
      });
      router.push("/dashboard");
    } catch (error) {
      console.error("Failed to complete workout:", error);
    }
  };

  const handleAddSet = async (exerciseEntryId: number, setNumber: number) => {
    try {
      await apiClient.post(`/exercise-entry/${exerciseEntryId}/set`, {
        set_number: setNumber,
        weight_kg: null,
        reps: null,
        is_warmup: false,
      });
      // Refresh workout data using React Query
      await queryClient.invalidateQueries({ queryKey: ["workout-session", workoutId] });
    } catch (error) {
      console.error("Failed to add set:", error);
      alert("Failed to add set. Please try again.");
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">Loading workout...</div>
      </div>
    );
  }

  if (!workout) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">Workout not found</div>
      </div>
    );
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {workout.name || "Workout"}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {format(new Date(workout.started_at), "MMMM d, yyyy 'at' h:mm a")}
            </p>
          </div>
          <div className="flex space-x-2">
            {!workout.completed_at && (
              <button
                onClick={handleCompleteWorkout}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Complete Workout
              </button>
            )}
            <button
              onClick={() => router.back()}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Back
            </button>
          </div>
        </div>

        {/* Rest Timer */}
        {restTimer !== null && (
          <div className="mb-6 bg-indigo-50 border-2 border-indigo-500 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-indigo-900">Rest Timer</div>
                <div className="text-3xl font-bold text-indigo-600 mt-2">
                  {formatTime(restTimer)}
                </div>
              </div>
              <button
                onClick={stopRestTimer}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Stop
              </button>
            </div>
          </div>
        )}

        {/* Exercise Entries */}
        <div className="space-y-6">
          {workout.exercise_entries?.map((entry: any, entryIndex: number) => (
            <div key={entry.id} className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Exercise {entryIndex + 1}: {entry.exercise_name || `Exercise ${entry.exercise_id}` || "Unknown Exercise"}
              </h3>
              <div className="space-y-3">
                {entry.sets?.map((set: any, setIndex: number) => (
                  <div
                    key={set.id}
                    className="flex items-center space-x-4 p-3 border border-gray-200 rounded-lg"
                  >
                    <span className="text-sm font-medium text-gray-700 w-12">
                      Set {set.set_number}
                    </span>
                    <div className="flex-1 grid grid-cols-3 gap-4">
                      <div>
                        <label className="text-xs text-gray-500">Weight (kg)</label>
                        <input
                          type="number"
                          value={set.weight_kg || ""}
                          onChange={async (e) => {
                            try {
                              await apiClient.patch(`/set-entry/${set.id}`, {
                                weight_kg: parseFloat(e.target.value) || null,
                              });
                              await queryClient.invalidateQueries({ queryKey: ["workout-session", workoutId] });
                            } catch (error) {
                              console.error("Failed to update weight:", error);
                            }
                          }}
                          className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                          placeholder="0"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-gray-500">Reps</label>
                        <input
                          type="number"
                          value={set.reps || ""}
                          onChange={async (e) => {
                            try {
                              await apiClient.patch(`/set-entry/${set.id}`, {
                                reps: parseInt(e.target.value) || null,
                              });
                              await queryClient.invalidateQueries({ queryKey: ["workout-session", workoutId] });
                            } catch (error) {
                              console.error("Failed to update reps:", error);
                            }
                          }}
                          className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                          placeholder="0"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-gray-500">RIR</label>
                        <input
                          type="number"
                          value={set.rir || ""}
                          onChange={async (e) => {
                            try {
                              await apiClient.patch(`/set-entry/${set.id}`, {
                                rir: parseInt(e.target.value) || null,
                              });
                              await queryClient.invalidateQueries({ queryKey: ["workout-session", workoutId] });
                            } catch (error) {
                              console.error("Failed to update RIR:", error);
                            }
                          }}
                          className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                          placeholder="0"
                        />
                      </div>
                    </div>
                    {set.rest_seconds && (
                      <button
                        onClick={() => startRestTimer(set.rest_seconds)}
                        className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                      >
                        Rest {Math.floor(set.rest_seconds / 60)}m
                      </button>
                    )}
                  </div>
                ))}
                <button
                  onClick={() => handleAddSet(entry.id, (entry.sets?.length || 0) + 1)}
                  className="w-full px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-indigo-500 hover:text-indigo-500"
                >
                  + Add Set
                </button>
              </div>
            </div>
          ))}
        </div>

        {(!workout.exercise_entries || workout.exercise_entries.length === 0) && (
          <div className="text-center py-12 text-gray-500">
            No exercises in this workout yet.
          </div>
        )}
      </div>
    </div>
  );
}

