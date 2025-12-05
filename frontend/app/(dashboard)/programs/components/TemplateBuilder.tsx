"use client";

import { useState } from "react";
import { useExercises } from "@/lib/hooks/use-exercises";
import { apiClient } from "@/lib/api/client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { generateSetsForPeriodization, type SetConfig } from "@/lib/utils/periodization";

interface TemplateExercise {
  exercise_id: number;
  exercise_name: string;
  sets: SetConfig[];
  notes?: string;
  order: number;
}

interface TemplateBuilderProps {
  onClose: () => void;
  onTemplateCreated?: (templateId: number) => void;
  periodizationType?: "linear" | "undulating" | "block";
  programWeeks?: number;
}

export default function TemplateBuilder({
  onClose,
  onTemplateCreated,
  periodizationType = "linear",
  programWeeks = 4,
}: TemplateBuilderProps) {
  const [templateName, setTemplateName] = useState("");
  const [templateDescription, setTemplateDescription] = useState("");
  const [estimatedDuration, setEstimatedDuration] = useState<number | null>(null);
  const [exercises, setExercises] = useState<TemplateExercise[]>([]);
  const [selectedExerciseId, setSelectedExerciseId] = useState<number | null>(null);
  const [weightType, setWeightType] = useState<"static" | "percentage">("percentage");
  const [showExerciseSelector, setShowExerciseSelector] = useState(false);

  const { data: exercisesList = [], isLoading: exercisesLoading } = useExercises();
  const queryClient = useQueryClient();

  const createTemplate = useMutation({
    mutationFn: async (templateData: any) => {
      const response = await apiClient.post("/workout-template", templateData);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["workout-templates"] });
      if (onTemplateCreated) {
        onTemplateCreated(data.id);
      }
      onClose();
    },
  });

  const handleAddExercise = () => {
    if (!selectedExerciseId) return;

    const exercise = exercisesList.find((e: any) => e.id === selectedExerciseId);
    if (!exercise) return;

    // Generate sets based on periodization type
    const sets = generateSetsForPeriodization(periodizationType, 1, programWeeks);

    const newExercise: TemplateExercise = {
      exercise_id: selectedExerciseId,
      exercise_name: exercise.name,
      sets,
      order: exercises.length,
      notes: "",
    };

    setExercises([...exercises, newExercise]);
    setSelectedExerciseId(null);
    setShowExerciseSelector(false);
  };

  const handleAddSet = (exerciseIndex: number) => {
    const updatedExercises = [...exercises];
    const exercise = updatedExercises[exerciseIndex];
    const newSetNumber = exercise.sets.length + 1;

    exercise.sets.push({
      set_number: newSetNumber,
      reps: 8,
      percentage_of_1rm: weightType === "percentage" ? 75 : null,
      weight_kg: weightType === "static" ? null : null,
      rest_seconds: 180,
      is_warmup: false,
    });

    setExercises(updatedExercises);
  };

  const handleRemoveSet = (exerciseIndex: number, setIndex: number) => {
    const updatedExercises = [...exercises];
    updatedExercises[exerciseIndex].sets.splice(setIndex, 1);
    // Renumber sets
    updatedExercises[exerciseIndex].sets.forEach((set, idx) => {
      set.set_number = idx + 1;
    });
    setExercises(updatedExercises);
  };

  const handleUpdateSet = (
    exerciseIndex: number,
    setIndex: number,
    field: keyof SetConfig,
    value: any
  ) => {
    const updatedExercises = [...exercises];
    const set = updatedExercises[exerciseIndex].sets[setIndex];
    (set as any)[field] = value;
    setExercises(updatedExercises);
  };

  const handleRemoveExercise = (index: number) => {
    setExercises(exercises.filter((_, i) => i !== index).map((e, i) => ({ ...e, order: i })));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!templateName.trim() || exercises.length === 0) {
      alert("Please provide a template name and at least one exercise");
      return;
    }

    const templateData = {
      name: templateName,
      description: templateDescription || null,
      estimated_duration_minutes: estimatedDuration,
      is_public: false,
      template_exercises: exercises.map((ex) => ({
        exercise_id: ex.exercise_id,
        notes: ex.notes || null,
        order: ex.order,
        template_sets: ex.sets.map((set, setIdx) => ({
          set_number: set.set_number && set.set_number > 0 ? set.set_number : setIdx + 1,
          reps: set.reps && set.reps > 0 ? set.reps : null,
          weight_kg: set.weight_kg && set.weight_kg > 0 ? set.weight_kg : null,
          percentage_of_1rm: set.percentage_of_1rm && set.percentage_of_1rm > 0 ? set.percentage_of_1rm : null,
          rir: set.rir !== null && set.rir !== undefined ? set.rir : null,
          rpe: set.rpe !== null && set.rpe !== undefined ? set.rpe : null,
          rest_seconds: set.rest_seconds && set.rest_seconds > 0 ? set.rest_seconds : null,
          tempo: null,
          notes: null,
          is_warmup: set.is_warmup || false,
        })),
      })),
    };

    createTemplate.mutate(templateData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-strong">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-neutral-900">Create Workout Template</h2>
          <button
            onClick={onClose}
            className="text-neutral-500 hover:text-neutral-700 text-2xl leading-none"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Template Info */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Template Name *
              </label>
              <input
                type="text"
                required
                value={templateName}
                onChange={(e) => setTemplateName(e.target.value)}
                className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="e.g., Push Day, Pull Day"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Description</label>
              <textarea
                value={templateDescription}
                onChange={(e) => setTemplateDescription(e.target.value)}
                rows={2}
                className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Optional description..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">
                  Estimated Duration (minutes)
                </label>
                <input
                  type="number"
                  min="1"
                  value={estimatedDuration || ""}
                  onChange={(e) =>
                    setEstimatedDuration(e.target.value ? parseInt(e.target.value) : null)
                  }
                  className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Weight Type</label>
                <select
                  value={weightType}
                  onChange={(e) => setWeightType(e.target.value as "static" | "percentage")}
                  className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="percentage">Percentage of 1RM</option>
                  <option value="static">Static Weight</option>
                </select>
              </div>
            </div>
          </div>

          {/* Add Exercise */}
          <div className="border-t pt-4">
            <div className="flex items-center gap-2 mb-4">
              <select
                value={selectedExerciseId || ""}
                onChange={(e) => setSelectedExerciseId(e.target.value ? parseInt(e.target.value) : null)}
                className="flex-1 border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={exercisesLoading}
              >
                <option value="">Select an exercise...</option>
                {exercisesList.map((exercise: any) => (
                  <option key={exercise.id} value={exercise.id}>
                    {exercise.name}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={handleAddExercise}
                disabled={!selectedExerciseId}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Add Exercise
              </button>
            </div>
          </div>

          {/* Exercises List */}
          <div className="space-y-4">
            {exercises.map((exercise, exerciseIndex) => (
              <div key={exerciseIndex} className="border border-neutral-200 rounded-xl p-5 bg-white shadow-sm">
                <div className="flex justify-between items-center mb-4 pb-3 border-b border-neutral-200">
                  <div>
                    <h3 className="text-lg font-semibold text-neutral-900">{exercise.exercise_name}</h3>
                    <p className="text-xs text-neutral-500 mt-0.5">
                      {exercise.sets.length} {exercise.sets.length === 1 ? "set" : "sets"}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveExercise(exerciseIndex)}
                    className="px-3 py-1.5 text-sm font-medium text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    Remove Exercise
                  </button>
                </div>

                {/* Sets */}
                <div className="space-y-3">
                  {/* Header Row */}
                  <div className="grid grid-cols-12 gap-3 items-center pb-2 border-b border-neutral-200">
                    <div className="col-span-1 text-xs font-semibold text-neutral-500 uppercase tracking-wide">
                      Set
                    </div>
                    <div className="col-span-2 text-xs font-semibold text-neutral-500 uppercase tracking-wide">
                      Reps
                    </div>
                    <div className="col-span-2 text-xs font-semibold text-neutral-500 uppercase tracking-wide">
                      {weightType === "percentage" ? "% 1RM" : "Weight (kg)"}
                    </div>
                    <div className="col-span-2 text-xs font-semibold text-neutral-500 uppercase tracking-wide">
                      Rest (sec)
                    </div>
                    <div className="col-span-2 text-xs font-semibold text-neutral-500 uppercase tracking-wide">
                      Type
                    </div>
                    <div className="col-span-3 text-xs font-semibold text-neutral-500 uppercase tracking-wide">
                      Actions
                    </div>
                  </div>

                  {/* Sets List */}
                  {exercise.sets.map((set, setIndex) => (
                    <div
                      key={setIndex}
                      className="grid grid-cols-12 gap-3 items-center bg-white border border-neutral-200 rounded-lg p-3 hover:border-primary-300 transition-colors"
                    >
                      <div className="col-span-1">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-700 font-semibold text-sm">
                          {set.set_number}
                        </div>
                      </div>
                      <div className="col-span-2">
                        <label className="block text-xs text-neutral-600 mb-1">Reps</label>
                        <input
                          type="number"
                          min="1"
                          value={set.reps || ""}
                          onChange={(e) =>
                            handleUpdateSet(exerciseIndex, setIndex, "reps", e.target.value ? parseInt(e.target.value) : null)
                          }
                          className="w-full border border-neutral-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          placeholder="10"
                        />
                      </div>
                      {weightType === "percentage" ? (
                        <div className="col-span-2">
                          <label className="block text-xs text-neutral-600 mb-1">% of 1RM</label>
                          <div className="relative">
                            <input
                              type="number"
                              min="1"
                              max="100"
                              value={set.percentage_of_1rm || ""}
                              onChange={(e) =>
                                handleUpdateSet(
                                  exerciseIndex,
                                  setIndex,
                                  "percentage_of_1rm",
                                  e.target.value ? parseFloat(e.target.value) : null
                                )
                              }
                              className="w-full border border-neutral-300 rounded-lg px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                              placeholder="75"
                            />
                            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-neutral-500">%</span>
                          </div>
                        </div>
                      ) : (
                        <div className="col-span-2">
                          <label className="block text-xs text-neutral-600 mb-1">Weight</label>
                          <div className="relative">
                            <input
                              type="number"
                              min="0"
                              step="0.5"
                              value={set.weight_kg || ""}
                              onChange={(e) =>
                                handleUpdateSet(
                                  exerciseIndex,
                                  setIndex,
                                  "weight_kg",
                                  e.target.value ? parseFloat(e.target.value) : null
                                )
                              }
                              className="w-full border border-neutral-300 rounded-lg px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                              placeholder="100"
                            />
                            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-neutral-500">kg</span>
                          </div>
                        </div>
                      )}
                      <div className="col-span-2">
                        <label className="block text-xs text-neutral-600 mb-1">Rest</label>
                        <div className="relative">
                          <input
                            type="number"
                            min="0"
                            value={set.rest_seconds || ""}
                            onChange={(e) =>
                              handleUpdateSet(
                                exerciseIndex,
                                setIndex,
                                "rest_seconds",
                                e.target.value ? parseInt(e.target.value) : null
                              )
                            }
                            className="w-full border border-neutral-300 rounded-lg px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            placeholder="180"
                          />
                          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-neutral-500">sec</span>
                        </div>
                      </div>
                      <div className="col-span-2">
                        <label className="block text-xs text-neutral-600 mb-1">Type</label>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={set.is_warmup || false}
                            onChange={(e) =>
                              handleUpdateSet(exerciseIndex, setIndex, "is_warmup", e.target.checked)
                            }
                            className="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500 focus:ring-2"
                          />
                          <span className="text-sm text-neutral-700">Warmup</span>
                        </label>
                      </div>
                      <div className="col-span-3 flex items-end">
                        <button
                          type="button"
                          onClick={() => handleRemoveSet(exerciseIndex, setIndex)}
                          className="px-3 py-2 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          disabled={exercise.sets.length === 1}
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  ))}
                  
                  {/* Add Set Button */}
                  <button
                    type="button"
                    onClick={() => handleAddSet(exerciseIndex)}
                    className="w-full py-2 text-sm font-medium text-primary-600 hover:text-primary-800 hover:bg-primary-50 rounded-lg border-2 border-dashed border-primary-300 transition-colors"
                  >
                    + Add Set
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Submit */}
          <div className="flex space-x-2 pt-4 border-t">
            <button
              type="submit"
              disabled={createTemplate.isPending || !templateName.trim() || exercises.length === 0}
              className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createTemplate.isPending ? "Creating..." : "Create Template"}
            </button>
            <button type="button" onClick={onClose} className="flex-1 btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

