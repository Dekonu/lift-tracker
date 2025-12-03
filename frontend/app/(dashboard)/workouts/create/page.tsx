"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useExercises } from "@/lib/hooks/use-exercises";
import { useCreateWorkoutSession } from "@/lib/hooks/use-workouts";
import { apiClient } from "@/lib/api/client";
import { format } from "date-fns";

interface ExerciseInstance {
  exercise_id: number;
  order: number;
  sets: Array<{
    weight_value: number;
    weight_type: "percentage" | "static";
    unit: "lbs" | "kg";
    reps?: number;
    rir?: number;
    rest_time_seconds?: number;
    notes?: string;
  }>;
}

export default function CreateWorkoutPage() {
  const router = useRouter();
  const { data: exercises = [], isLoading: exercisesLoading } = useExercises();
  const createWorkout = useCreateWorkoutSession();
  const [workoutDate, setWorkoutDate] = useState(new Date());
  const [selectedExercises, setSelectedExercises] = useState<ExerciseInstance[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleAddExercise = (exerciseId: number) => {
    const exercise = exercises.find((e: any) => e.id === exerciseId);
    if (!exercise) return;

    setSelectedExercises([
      ...selectedExercises,
      {
        exercise_id: exerciseId,
        order: selectedExercises.length,
        sets: [{ weight_value: 0, weight_type: "static", unit: "kg", reps: 10 }],
      },
    ]);
  };

  const handleAddSet = (exerciseIndex: number) => {
    const updated = [...selectedExercises];
    updated[exerciseIndex].sets.push({
      weight_value: 0,
      weight_type: "static",
      unit: "kg",
      reps: 10,
    });
    setSelectedExercises(updated);
  };

  const handleRemoveExercise = (index: number) => {
    setSelectedExercises(selectedExercises.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSaving(true);

    try {
      // Create workout session
      const sessionResponse = await createWorkout.mutateAsync({
        started_at: workoutDate.toISOString(),
        name: null,
      });

      const sessionId = sessionResponse.id;

      // Add exercise entries and sets
      for (let i = 0; i < selectedExercises.length; i++) {
        const exerciseInstance = selectedExercises[i];

        try {
          const entryResponse = await apiClient.post(`/workout-session/${sessionId}/exercise-entry`, {
            workout_session_id: sessionId,
            exercise_id: exerciseInstance.exercise_id,
            order: exerciseInstance.order,
          });

          const exerciseEntryId = entryResponse.data.id;

          // Add sets
          for (let setIndex = 0; setIndex < exerciseInstance.sets.length; setIndex++) {
            const set = exerciseInstance.sets[setIndex];
            let weight_kg: number | null = null;
            if (set.weight_type === "static") {
              if (set.unit === "kg") {
                weight_kg = set.weight_value;
              } else if (set.unit === "lbs") {
                weight_kg = set.weight_value * 0.453592;
              }
            }

            const setEntry = {
              exercise_entry_id: exerciseEntryId,
              set_number: setIndex + 1,
              weight_kg: weight_kg,
              reps: set.reps || null,
              rir: set.rir || null,
              percentage_of_1rm: set.weight_type === "percentage" ? set.weight_value : null,
              rest_seconds: set.rest_time_seconds || null,
              notes: set.notes || null,
              is_warmup: false,
            };

            await apiClient.post(`/exercise-entry/${exerciseEntryId}/set`, setEntry);
          }
        } catch (entryErr: any) {
          console.error(`Error adding exercise entry ${i + 1}:`, entryErr);
          throw new Error(`Failed to add exercise entry: ${entryErr.response?.data?.detail || entryErr.message}`);
        }
      }

      // Navigate to workout detail page
      router.push(`/workouts/${sessionId}`);
    } catch (err: any) {
      console.error("Error creating workout:", err);
      setError(err.message || err.response?.data?.detail || "Failed to create workout");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Workout</h2>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Workout Date & Time
            </label>
            <input
              type="datetime-local"
              value={format(workoutDate, "yyyy-MM-dd'T'HH:mm")}
              onChange={(e) => setWorkoutDate(new Date(e.target.value))}
              className="block w-full border border-gray-300 rounded-md px-3 py-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Add Exercises
            </label>
            {exercisesLoading ? (
              <div>Loading exercises...</div>
            ) : (
              <select
                onChange={(e) => {
                  if (e.target.value) {
                    handleAddExercise(parseInt(e.target.value));
                    e.target.value = "";
                  }
                }}
                className="block w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="">Select an exercise...</option>
                {exercises
                  .filter((e: any) => e.enabled)
                  .map((exercise: any) => (
                    <option key={exercise.id} value={exercise.id}>
                      {exercise.name}
                    </option>
                  ))}
              </select>
            )}
          </div>

          <div className="space-y-4">
            {selectedExercises.map((exerciseInstance, exerciseIndex) => {
              const exercise = exercises.find((e: any) => e.id === exerciseInstance.exercise_id);
              return (
                <div key={exerciseIndex} className="bg-white p-4 rounded-lg border border-gray-200">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="font-medium text-gray-900">
                      {exercise?.name || "Unknown Exercise"}
                    </h3>
                    <button
                      type="button"
                      onClick={() => handleRemoveExercise(exerciseIndex)}
                      className="text-red-600 hover:text-red-700 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                  <div className="space-y-2">
                    {exerciseInstance.sets.map((set, setIndex) => (
                      <div key={setIndex} className="flex items-center space-x-2">
                        <span className="text-sm text-gray-600 w-8">Set {setIndex + 1}</span>
                        <input
                          type="number"
                          placeholder="Weight"
                          value={set.weight_value || ""}
                          onChange={(e) => {
                            const updated = [...selectedExercises];
                            updated[exerciseIndex].sets[setIndex].weight_value = parseFloat(e.target.value) || 0;
                            setSelectedExercises(updated);
                          }}
                          className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm"
                        />
                        <select
                          value={set.unit}
                          onChange={(e) => {
                            const updated = [...selectedExercises];
                            updated[exerciseIndex].sets[setIndex].unit = e.target.value as "kg" | "lbs";
                            setSelectedExercises(updated);
                          }}
                          className="border border-gray-300 rounded px-2 py-1 text-sm"
                        >
                          <option value="kg">kg</option>
                          <option value="lbs">lbs</option>
                        </select>
                        <input
                          type="number"
                          placeholder="Reps"
                          value={set.reps || ""}
                          onChange={(e) => {
                            const updated = [...selectedExercises];
                            updated[exerciseIndex].sets[setIndex].reps = parseInt(e.target.value) || undefined;
                            setSelectedExercises(updated);
                          }}
                          className="w-20 border border-gray-300 rounded px-2 py-1 text-sm"
                        />
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={() => handleAddSet(exerciseIndex)}
                      className="text-sm text-indigo-600 hover:text-indigo-500"
                    >
                      + Add Set
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {selectedExercises.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Add exercises to get started
            </div>
          )}

          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={saving || selectedExercises.length === 0}
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {saving ? "Creating..." : "Create Workout"}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

