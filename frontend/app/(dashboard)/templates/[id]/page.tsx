"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useExercises } from "@/lib/hooks/use-exercises";
import Link from "next/link";

export default function TemplateDetailPage() {
  const params = useParams();
  const router = useRouter();
  const templateId = Number(params.id);
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

  const deleteTemplate = useMutation({
    mutationFn: async () => {
      await apiClient.delete(`/workout-template/${templateId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workout-templates"] });
      router.push("/templates");
    },
  });

  const handleDelete = () => {
    if (confirm(`Are you sure you want to delete "${template?.name}"? This action cannot be undone.`)) {
      deleteTemplate.mutate();
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  if (!template) {
    return (
      <div className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="text-center py-12 card">
          <p className="text-neutral-600 mb-4">Template not found.</p>
          <Link href="/templates" className="btn-primary">
            Back to Templates
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
      <div className="px-4 sm:px-0">
        <div className="mb-6">
          <Link
            href="/templates"
            className="text-primary-600 hover:text-primary-700 text-sm font-medium mb-4 inline-block"
          >
            ← Back to Templates
          </Link>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-neutral-900 mb-2">{template.name}</h1>
              {template.description && (
                <p className="text-neutral-600">{template.description}</p>
              )}
            </div>
            <button
              onClick={handleDelete}
              disabled={deleteTemplate.isPending}
              className="btn-secondary text-red-600 hover:text-red-700 disabled:opacity-50"
            >
              Delete Template
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
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
          <h2 className="text-xl font-semibold text-neutral-900 mb-4">Exercises</h2>
          {template.template_exercises && template.template_exercises.length > 0 ? (
            <div className="space-y-6">
              {template.template_exercises
                .sort((a: any, b: any) => a.order - b.order)
                .map((te: any, idx: number) => {
                  const exercise = exercises.find((e: any) => e.id === te.exercise_id);
                  return (
                    <div key={idx} className="border border-neutral-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold text-neutral-900">
                            {exercise?.name || `Exercise ${te.exercise_id}`}
                          </h3>
                          {te.notes && (
                            <p className="text-sm text-neutral-600 mt-1">{te.notes}</p>
                          )}
                        </div>
                        <span className="text-xs text-neutral-500">
                          Order: {te.order + 1}
                        </span>
                      </div>

                      {/* Sets */}
                      {te.template_sets && te.template_sets.length > 0 && (
                        <div className="mt-3">
                          <div className="text-xs font-medium text-neutral-700 mb-2">Sets:</div>
                          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
                            {te.template_sets
                              .sort((a: any, b: any) => a.set_number - b.set_number)
                              .map((set: any, setIdx: number) => (
                                <div
                                  key={setIdx}
                                  className="bg-neutral-50 border border-neutral-200 rounded p-2 text-sm"
                                >
                                  <div className="font-medium text-neutral-900 mb-1">
                                    Set {set.set_number}
                                  </div>
                                  {set.reps && (
                                    <div className="text-neutral-600">
                                      <span className="font-medium">Reps:</span> {set.reps}
                                    </div>
                                  )}
                                  {set.weight_kg && (
                                    <div className="text-neutral-600">
                                      <span className="font-medium">Weight:</span> {set.weight_kg} kg
                                    </div>
                                  )}
                                  {set.percentage_of_1rm && (
                                    <div className="text-neutral-600">
                                      <span className="font-medium">%1RM:</span> {set.percentage_of_1rm}%
                                    </div>
                                  )}
                                  {set.rpe && (
                                    <div className="text-neutral-600">
                                      <span className="font-medium">RPE:</span> {set.rpe}
                                    </div>
                                  )}
                                  {set.rir !== null && set.rir !== undefined && (
                                    <div className="text-neutral-600">
                                      <span className="font-medium">RIR:</span> {set.rir}
                                    </div>
                                  )}
                                  {set.rest_seconds && (
                                    <div className="text-neutral-600">
                                      <span className="font-medium">Rest:</span> {set.rest_seconds}s
                                    </div>
                                  )}
                                  {set.is_warmup && (
                                    <span className="inline-block mt-1 px-1.5 py-0.5 text-xs bg-yellow-100 text-yellow-800 rounded">
                                      Warmup
                                    </span>
                                  )}
                                </div>
                              ))}
                          </div>
                        </div>
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
      </div>
    </div>
  );
}

