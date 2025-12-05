"use client";

import { useState, useMemo } from "react";
import { useWorkoutTemplates } from "@/lib/hooks/use-programs";
import { useExercises } from "@/lib/hooks/use-exercises";
import { apiClient } from "@/lib/api/client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import TemplateBuilder from "../programs/components/TemplateBuilder";

export default function TemplatesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMuscleGroup, setSelectedMuscleGroup] = useState<string>("");
  const [showPublicOnly, setShowPublicOnly] = useState(false);
  const [showTemplateBuilder, setShowTemplateBuilder] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<number | null>(null);
  const { data: templates = [], isLoading } = useWorkoutTemplates();
  const { data: exercises = [] } = useExercises();
  const queryClient = useQueryClient();

  // Get unique muscle groups from exercises
  const muscleGroups = useMemo(() => {
    const groups = new Set<string>();
    exercises.forEach((ex: any) => {
      if (ex.primary_muscle_group) {
        groups.add(ex.primary_muscle_group);
      }
    });
    return Array.from(groups).sort();
  }, [exercises]);

  // Filter templates
  const filteredTemplates = useMemo(() => {
    return templates.filter((template: any) => {
      const matchesSearch =
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description?.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesMuscleGroup = !selectedMuscleGroup || 
        template.template_exercises?.some((te: any) => {
          const exercise = exercises.find((e: any) => e.id === te.exercise_id);
          return exercise?.primary_muscle_group === selectedMuscleGroup;
        });
      
      const matchesVisibility = !showPublicOnly || template.is_public;

      return matchesSearch && matchesMuscleGroup && matchesVisibility;
    });
  }, [templates, searchQuery, selectedMuscleGroup, showPublicOnly, exercises]);

  const deleteTemplate = useMutation({
    mutationFn: async (templateId: number) => {
      await apiClient.delete(`/workout-template/${templateId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workout-templates"] });
    },
  });

  const handleDelete = async (templateId: number, templateName: string) => {
    if (confirm(`Are you sure you want to delete "${templateName}"? This action cannot be undone.`)) {
      await deleteTemplate.mutateAsync(templateId);
    }
  };

  const handleTemplateCreated = (templateId: number) => {
    setShowTemplateBuilder(false);
    queryClient.invalidateQueries({ queryKey: ["workout-templates"] });
  };

  return (
    <div className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
      <div className="px-4 sm:px-0">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <h1 className="text-3xl font-bold text-neutral-900">Workout Templates</h1>
            <button
              onClick={() => setShowTemplateBuilder(true)}
              className="btn-primary"
            >
              + Create Template
            </button>
          </div>
          <p className="text-neutral-600">
            Create, manage, and organize your workout templates. Templates can be assigned to programs.
          </p>
        </div>

        {/* Search and Filters */}
        <div className="card p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Search Templates
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name or description..."
                className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Muscle Group
              </label>
              <select
                value={selectedMuscleGroup}
                onChange={(e) => setSelectedMuscleGroup(e.target.value)}
                className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">All Muscle Groups</option>
                {muscleGroups.map((group) => (
                  <option key={group} value={group}>
                    {group}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showPublicOnly}
                  onChange={(e) => setShowPublicOnly(e.target.checked)}
                  className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-neutral-700">Show public templates only</span>
              </label>
            </div>
          </div>
        </div>

        {/* Templates Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : filteredTemplates.length === 0 ? (
          <div className="text-center py-12 card">
            <p className="text-neutral-600 mb-4">
              {searchQuery || selectedMuscleGroup || showPublicOnly
                ? "No templates match your filters."
                : "No templates yet. Create your first template to get started!"}
            </p>
            {!searchQuery && !selectedMuscleGroup && !showPublicOnly && (
              <button
                onClick={() => setShowTemplateBuilder(true)}
                className="btn-primary"
              >
                Create Template
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template: any) => {
              const exerciseCount = template.template_exercises?.length || 0;
              const totalSets = template.template_exercises?.reduce(
                (sum: number, te: any) => sum + (te.template_sets?.length || 0),
                0
              ) || 0;

              return (
                <div
                  key={template.id}
                  className="card p-6 hover:shadow-lg transition-shadow"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-neutral-900 mb-1">
                        {template.name}
                      </h3>
                      {template.is_public && (
                        <span className="inline-block px-2 py-0.5 text-xs font-medium bg-primary-100 text-primary-800 rounded">
                          Public
                        </span>
                      )}
                    </div>
                  </div>

                  {template.description && (
                    <p className="text-sm text-neutral-600 mb-4 line-clamp-2">
                      {template.description}
                    </p>
                  )}

                  <div className="space-y-2 mb-4">
                    <div className="text-sm">
                      <span className="font-medium text-neutral-700">Exercises:</span>{" "}
                      <span className="text-neutral-600">{exerciseCount}</span>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium text-neutral-700">Total Sets:</span>{" "}
                      <span className="text-neutral-600">{totalSets}</span>
                    </div>
                    {template.estimated_duration_minutes && (
                      <div className="text-sm">
                        <span className="font-medium text-neutral-700">Duration:</span>{" "}
                        <span className="text-neutral-600">
                          {template.estimated_duration_minutes} min
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Exercise Preview */}
                  {template.template_exercises && template.template_exercises.length > 0 && (
                    <div className="mb-4">
                      <div className="text-xs font-medium text-neutral-700 mb-2">
                        Exercises:
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {template.template_exercises.slice(0, 3).map((te: any, idx: number) => {
                          const exercise = exercises.find((e: any) => e.id === te.exercise_id);
                          return (
                            <span
                              key={idx}
                              className="inline-block px-2 py-0.5 text-xs bg-neutral-100 text-neutral-700 rounded"
                            >
                              {exercise?.name || `Exercise ${te.exercise_id}`}
                            </span>
                          );
                        })}
                        {template.template_exercises.length > 3 && (
                          <span className="inline-block px-2 py-0.5 text-xs bg-neutral-100 text-neutral-700 rounded">
                            +{template.template_exercises.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-2 pt-4 border-t">
                    <Link
                      href={`/templates/${template.id}`}
                      className="flex-1 btn-secondary text-sm text-center"
                    >
                      View Details
                    </Link>
                    <button
                      onClick={() => handleDelete(template.id, template.name)}
                      disabled={deleteTemplate.isPending}
                      className="btn-secondary text-sm text-red-600 hover:text-red-700 disabled:opacity-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Template Builder Modal */}
        {showTemplateBuilder && (
          <TemplateBuilder
            onClose={() => setShowTemplateBuilder(false)}
            onTemplateCreated={handleTemplateCreated}
          />
        )}
      </div>
    </div>
  );
}

