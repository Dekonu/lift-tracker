"use client";

import { useState, useEffect } from "react";
import { useWorkoutTemplates } from "@/lib/hooks/use-programs";
import { apiClient } from "@/lib/api/client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import TemplateBuilder from "./TemplateBuilder";

interface ProgramWeekEditorProps {
  programId: number;
  durationWeeks: number;
  daysPerWeek: number;
  periodizationType: string;
  onClose: () => void;
}

export default function ProgramWeekEditor({
  programId,
  durationWeeks,
  daysPerWeek,
  periodizationType,
  onClose,
}: ProgramWeekEditorProps) {
  const { data: templates = [] } = useWorkoutTemplates();
  const [weekAssignments, setWeekAssignments] = useState<Record<number, number | null>>({});
  const [showTemplateBuilder, setShowTemplateBuilder] = useState(false);
  const queryClient = useQueryClient();

  // Fetch existing program weeks
  const { data: existingWeeks = [] } = useQuery({
    queryKey: ["program-weeks", programId],
    queryFn: async () => {
      const response = await apiClient.get(`/program/${programId}/weeks`);
      return response.data.data || [];
    },
  });

  // Initialize week assignments from existing data
  useEffect(() => {
    const assignments: Record<number, number | null> = {};
    existingWeeks.forEach((week: any) => {
      assignments[week.week_number] = week.workout_template_id || null;
    });
    setWeekAssignments(assignments);
  }, [existingWeeks]);

  const addWeek = useMutation({
    mutationFn: async (weekData: { week_number: number; workout_template_id: number | null }) => {
      const response = await apiClient.post(`/program/${programId}/week`, weekData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["program-weeks", programId] });
    },
  });

  const handleAssignTemplate = async (weekNumber: number, templateId: number | null) => {
    setWeekAssignments({ ...weekAssignments, [weekNumber]: templateId });

    // Check if week already exists
    const existingWeek = existingWeeks.find((w: any) => w.week_number === weekNumber);

    if (existingWeek) {
      // Update existing week
      await apiClient.patch(`/program/${programId}/week/${existingWeek.id}`, {
        workout_template_id: templateId,
      });
    } else {
      // Create new week
      await addWeek.mutateAsync({
        week_number: weekNumber,
        workout_template_id: templateId,
      });
    }
  };

  const handleTemplateCreated = (templateId: number) => {
    setShowTemplateBuilder(false);
    queryClient.invalidateQueries({ queryKey: ["workout-templates"] });
    // Optionally assign to current week being edited
  };

  // Generate week grid
  const weeks = Array.from({ length: durationWeeks }, (_, i) => i + 1);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl p-6 max-w-6xl w-full max-h-[90vh] overflow-y-auto shadow-strong">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900">Program Week Schedule</h2>
            <p className="text-sm text-neutral-600 mt-1">
              Assign workout templates to each week ({durationWeeks} weeks, {daysPerWeek} days/week)
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

        {/* Week Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {weeks.map((weekNumber) => (
            <div key={weekNumber} className="border border-neutral-200 rounded-lg p-4">
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-semibold text-neutral-900">Week {weekNumber}</h3>
                <span className="text-xs text-neutral-500">
                  {daysPerWeek} {daysPerWeek === 1 ? "day" : "days"}
                </span>
              </div>

              <select
                value={weekAssignments[weekNumber] || ""}
                onChange={(e) =>
                  handleAssignTemplate(
                    weekNumber,
                    e.target.value ? parseInt(e.target.value) : null
                  )
                }
                className="w-full border border-neutral-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">No template assigned</option>
                {templates.map((template: any) => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))}
              </select>

              {weekAssignments[weekNumber] && (
                <div className="mt-2 text-xs text-neutral-600">
                  {templates.find((t: any) => t.id === weekAssignments[weekNumber])?.description ||
                    "Template assigned"}
                </div>
              )}
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

