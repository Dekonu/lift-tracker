"use client";

import { useState, useEffect } from "react";
import { useWorkoutTemplates } from "@/lib/hooks/use-programs";
import { apiClient } from "@/lib/api/client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import TemplateBuilder from "./TemplateBuilder";

interface ProgramDayEditorProps {
  programId: number;
  durationWeeks: number;
  daysPerWeek: number;
  periodizationType: string;
  onClose: () => void;
}

interface DayAssignment {
  id?: number;
  week_number: number;
  day_number: number;
  workout_template_id: number;
  order: number;
}

export default function ProgramDayEditor({
  programId,
  durationWeeks,
  daysPerWeek,
  periodizationType,
  onClose,
}: ProgramDayEditorProps) {
  const { data: templates = [] } = useWorkoutTemplates();
  const [dayAssignments, setDayAssignments] = useState<Record<string, DayAssignment[]>>({});
  const [showTemplateBuilder, setShowTemplateBuilder] = useState(false);
  const queryClient = useQueryClient();

  // Fetch existing day assignments
  const { data: existingAssignments = [] } = useQuery({
    queryKey: ["program-day-assignments", programId],
    queryFn: async () => {
      const response = await apiClient.get(`/program/${programId}/days`);
      return response.data.data || [];
    },
  });

  // Initialize day assignments from existing data
  useEffect(() => {
    const assignments: Record<string, DayAssignment[]> = {};
    existingAssignments.forEach((assignment: any) => {
      const key = `${assignment.week_number}-${assignment.day_number}`;
      if (!assignments[key]) {
        assignments[key] = [];
      }
      assignments[key].push({
        id: assignment.id,
        week_number: assignment.week_number,
        day_number: assignment.day_number,
        workout_template_id: assignment.workout_template_id,
        order: assignment.order || 0,
      });
    });
    // Sort by order
    Object.keys(assignments).forEach((key) => {
      assignments[key].sort((a, b) => a.order - b.order);
    });
    setDayAssignments(assignments);
  }, [existingAssignments]);

  const addDayAssignment = useMutation({
    mutationFn: async (assignmentData: {
      week_number: number;
      day_number: number;
      workout_template_id: number;
      order: number;
    }) => {
      const response = await apiClient.post(`/program/${programId}/day`, {
        ...assignmentData,
        program_id: programId,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["program-day-assignments", programId] });
    },
  });

  const updateDayAssignment = useMutation({
    mutationFn: async ({ assignmentId, data }: { assignmentId: number; data: any }) => {
      const response = await apiClient.patch(`/program/${programId}/day/${assignmentId}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["program-day-assignments", programId] });
    },
  });

  const deleteDayAssignment = useMutation({
    mutationFn: async (assignmentId: number) => {
      await apiClient.delete(`/program/${programId}/day/${assignmentId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["program-day-assignments", programId] });
    },
  });

  const handleAddTemplate = async (weekNumber: number, dayNumber: number, templateId: number) => {
    const key = `${weekNumber}-${dayNumber}`;
    const existing = dayAssignments[key] || [];
    const order = existing.length;

    await addDayAssignment.mutateAsync({
      week_number: weekNumber,
      day_number: dayNumber,
      workout_template_id: templateId,
      order,
    });
  };

  const handleRemoveTemplate = async (assignmentId: number) => {
    await deleteDayAssignment.mutateAsync(assignmentId);
  };

  const handleTemplateCreated = (templateId: number) => {
    setShowTemplateBuilder(false);
    queryClient.invalidateQueries({ queryKey: ["workout-templates"] });
  };

  // Generate week and day grid
  const weeks = Array.from({ length: durationWeeks }, (_, i) => i + 1);
  const days = Array.from({ length: daysPerWeek }, (_, i) => i + 1);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl p-6 max-w-7xl w-full max-h-[90vh] overflow-y-auto shadow-strong">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900">Program Schedule</h2>
            <p className="text-sm text-neutral-600 mt-1">
              Assign workout templates to specific days (Days 1-{daysPerWeek}) for each week
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowTemplateBuilder(true)}
              className="btn-secondary text-sm"
            >
              + New Template
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

        {/* Periodization Info */}
        <div className="mb-6 p-4 bg-primary-50 rounded-lg">
          <h3 className="font-semibold text-neutral-900 mb-2">
            Periodization: <span className="capitalize">{periodizationType}</span>
          </h3>
          <p className="text-sm text-neutral-600">
            {periodizationType === "linear" &&
              "Intensity increases and volume decreases progressively over time."}
            {periodizationType === "undulating" &&
              "Volume and intensity vary within each week for optimal adaptation."}
            {periodizationType === "block" &&
              "Focused training blocks targeting specific adaptations (accumulation → transmutation → realization)."}
          </p>
        </div>

        {/* Week and Day Grid */}
        <div className="space-y-6">
          {weeks.map((weekNumber) => (
            <div key={weekNumber} className="border border-neutral-200 rounded-lg p-4">
              <h3 className="font-semibold text-neutral-900 mb-4 text-lg">Week {weekNumber}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {days.map((dayNumber) => {
                  const key = `${weekNumber}-${dayNumber}`;
                  const assignments = dayAssignments[key] || [];

                  return (
                    <div key={dayNumber} className="border border-neutral-200 rounded-lg p-3 bg-neutral-50">
                      <div className="flex justify-between items-center mb-2">
                        <h4 className="font-medium text-neutral-900">Day {dayNumber}</h4>
                        <span className="text-xs text-neutral-500">
                          {assignments.length} {assignments.length === 1 ? "workout" : "workouts"}
                        </span>
                      </div>

                      {/* Existing Templates */}
                      <div className="space-y-2 mb-2">
                        {assignments.map((assignment) => {
                          const template = templates.find(
                            (t: any) => t.id === assignment.workout_template_id
                          );
                          return (
                            <div
                              key={assignment.id}
                              className="flex items-center justify-between bg-white border border-neutral-200 rounded px-2 py-1.5 text-sm"
                            >
                              <span className="truncate flex-1">{template?.name || "Unknown"}</span>
                              <button
                                onClick={() => assignment.id && handleRemoveTemplate(assignment.id)}
                                className="text-red-600 hover:text-red-800 ml-2 text-xs"
                                title="Remove"
                              >
                                ×
                              </button>
                            </div>
                          );
                        })}
                      </div>

                      {/* Add Template Dropdown */}
                      <select
                        value=""
                        onChange={(e) => {
                          if (e.target.value) {
                            handleAddTemplate(weekNumber, dayNumber, parseInt(e.target.value));
                            e.target.value = "";
                          }
                        }}
                        className="w-full border border-neutral-300 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="">+ Add workout</option>
                        {templates.map((template: any) => (
                          <option key={template.id} value={template.id}>
                            {template.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-end mt-6 pt-4 border-t">
          <button onClick={onClose} className="btn-primary">
            Done
          </button>
        </div>

        {/* Template Builder Modal */}
        {showTemplateBuilder && (
          <TemplateBuilder
            onClose={() => setShowTemplateBuilder(false)}
            onTemplateCreated={handleTemplateCreated}
            periodizationType={periodizationType as "linear" | "undulating" | "block"}
            programWeeks={durationWeeks}
          />
        )}
      </div>
    </div>
  );
}

