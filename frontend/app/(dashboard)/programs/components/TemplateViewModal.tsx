"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useExercises } from "@/lib/hooks/use-exercises";
import TemplateBuilder from "./TemplateBuilder";

interface TemplateViewModalProps {
  templateId: number;
  onClose: () => void;
}

export default function TemplateViewModal({ templateId, onClose }: TemplateViewModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  const queryClient = useQueryClient();
  const { data: exercises = [] } = useExercises();

  const { data: template, isLoading } = useQuery({
    queryKey: ["workout-template", templateId],
    queryFn: async () => {
      const response = await apiClient.get(`/workout-template/${templateId}`);
      return response.data;
    },
    enabled: !!templateId,
  });

  const updateTemplate = useMutation({
    mutationFn: async (updateData: { name?: string; description?: string; estimated_duration_minutes?: number }) => {
      const response = await apiClient.patch(`/workout-template/${templateId}`, updateData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workout-template", templateId] });
      queryClient.invalidateQueries({ queryKey: ["workout-templates"] });
      setIsEditing(false);
    },
  });

  const handleTemplateUpdated = () => {
    queryClient.invalidateQueries({ queryKey: ["workout-template", templateId] });
    queryClient.invalidateQueries({ queryKey: ["workout-templates"] });
    queryClient.invalidateQueries({ queryKey: ["program-day-assignments"] });
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!template) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="text-center py-12">
            <p className="text-neutral-600 mb-4">Template not found.</p>
            <button onClick={onClose} className="btn-primary">
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  // If editing, show TemplateBuilder
  if (isEditing) {
    return (
      <TemplateBuilder
        templateId={templateId}
        onClose={() => setIsEditing(false)}
        onTemplateCreated={handleTemplateUpdated}
        periodizationType="linear" // Default, can be enhanced later
        programWeeks={4} // Default, can be enhanced later
      />
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-strong">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900">{template.name}</h2>
            {template.description && (
              <p className="text-neutral-600 mt-1">{template.description}</p>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setIsEditing(true)}
              className="btn-secondary text-sm"
            >
              Edit Template
            </button>
            <button
              onClick={onClose}
              className="text-neutral-500 hover:text-neutral-700 text-2xl leading-none"
              aria-label="Close"
            >
              ×
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="card p-4">
            <div className="text-sm font-medium text-neutral-700 mb-1">Exercises</div>
            <div className="text-2xl font-bold text-neutral-900">
              {template.template_exercises?.length || 0}
            </div>
          </div>
          <div className="card p-4">
            <div className="text-sm font-medium text-neutral-700 mb-1">Total Sets</div>
            <div className="text-2xl font-bold text-neutral-900">
              {template.template_exercises?.reduce(
                (sum: number, te: any) => sum + (te.template_sets?.length || 0),
                0
              ) || 0}
            </div>
          </div>
          <div className="card p-4">
            <div className="text-sm font-medium text-neutral-700 mb-1">Estimated Duration</div>
            <div className="text-2xl font-bold text-neutral-900">
              {template.estimated_duration_minutes ? `${template.estimated_duration_minutes} min` : "N/A"}
            </div>
          </div>
        </div>

        {/* Exercises List */}
        <div className="card p-6">
          <h3 className="text-xl font-semibold text-neutral-900 mb-4">Exercises & Sets</h3>
          {template.template_exercises && template.template_exercises.length > 0 ? (
            <div className="space-y-6">
              {template.template_exercises
                .sort((a: any, b: any) => a.order - b.order)
                .map((te: any, idx: number) => {
                  const exercise = exercises.find((e: any) => e.id === te.exercise_id);
                  return (
                    <div key={idx} className="border border-neutral-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h4 className="font-semibold text-neutral-900 text-lg">
                            {exercise?.name || `Exercise ${te.exercise_id}`}
                          </h4>
                          {te.notes && (
                            <p className="text-sm text-neutral-600 mt-1">{te.notes}</p>
                          )}
                        </div>
                        <span className="text-xs text-neutral-500 bg-neutral-100 px-2 py-1 rounded">
                          Order: {te.order + 1}
                        </span>
                      </div>

                      {/* Sets */}
                      {te.template_sets && te.template_sets.length > 0 ? (
                        <div className="mt-4">
                          <div className="text-sm font-medium text-neutral-700 mb-3">Sets:</div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                            {te.template_sets
                              .sort((a: any, b: any) => a.set_number - b.set_number)
                              .map((set: any, setIdx: number) => (
                                <div
                                  key={setIdx}
                                  className="bg-neutral-50 border border-neutral-200 rounded-lg p-3"
                                >
                                  <div className="flex justify-between items-center mb-2">
                                    <div className="font-semibold text-neutral-900">
                                      Set {set.set_number}
                                    </div>
                                    {set.is_warmup && (
                                      <span className="px-2 py-0.5 text-xs bg-yellow-100 text-yellow-800 rounded">
                                        Warmup
                                      </span>
                                    )}
                                  </div>
                                  <div className="space-y-1 text-sm">
                                    {set.reps && (
                                      <div className="flex justify-between">
                                        <span className="text-neutral-600">Reps:</span>
                                        <span className="font-medium text-neutral-900">{set.reps}</span>
                                      </div>
                                    )}
                                    {set.weight_kg && (
                                      <div className="flex justify-between">
                                        <span className="text-neutral-600">Weight:</span>
                                        <span className="font-medium text-neutral-900">{set.weight_kg} kg</span>
                                      </div>
                                    )}
                                    {set.percentage_of_1rm && (
                                      <div className="flex justify-between">
                                        <span className="text-neutral-600">%1RM:</span>
                                        <span className="font-medium text-neutral-900">{set.percentage_of_1rm}%</span>
                                      </div>
                                    )}
                                    {set.rpe && (
                                      <div className="flex justify-between">
                                        <span className="text-neutral-600">RPE:</span>
                                        <span className="font-medium text-neutral-900">{set.rpe}</span>
                                      </div>
                                    )}
                                    {set.rir !== null && set.rir !== undefined && (
                                      <div className="flex justify-between">
                                        <span className="text-neutral-600">RIR:</span>
                                        <span className="font-medium text-neutral-900">{set.rir}</span>
                                      </div>
                                    )}
                                    {set.rest_seconds && (
                                      <div className="flex justify-between">
                                        <span className="text-neutral-600">Rest:</span>
                                        <span className="font-medium text-neutral-900">{set.rest_seconds}s</span>
                                      </div>
                                    )}
                                    {set.tempo && (
                                      <div className="flex justify-between">
                                        <span className="text-neutral-600">Tempo:</span>
                                        <span className="font-medium text-neutral-900">{set.tempo}</span>
                                      </div>
                                    )}
                                    {set.notes && (
                                      <div className="mt-2 pt-2 border-t border-neutral-200">
                                        <span className="text-xs text-neutral-500">{set.notes}</span>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              ))}
                          </div>
                        </div>
                      ) : (
                        <p className="text-sm text-neutral-500 mt-2">No sets defined for this exercise.</p>
                      )}
                    </div>
                  );
                })}
            </div>
          ) : (
            <p className="text-neutral-500 text-center py-8">
              No exercises in this template.
            </p>
          )}
        </div>

        <div className="flex justify-end mt-6 pt-4 border-t">
          <button onClick={onClose} className="btn-primary">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

