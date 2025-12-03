"use client";

import { useState } from "react";
import { usePrograms, useCreateProgram, useScheduleProgram, useWorkoutTemplates } from "@/lib/hooks/use-programs";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import Link from "next/link";

export default function ProgramsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState<number | null>(null);
  const { data: programs = [], isLoading } = usePrograms();
  const { data: templates = [] } = useWorkoutTemplates();
  const createProgram = useCreateProgram();
  const scheduleProgram = useScheduleProgram();

  // Fetch program weeks
  const { data: programWeeks = [] } = useQuery({
    queryKey: ["program-weeks", selectedProgram],
    queryFn: async () => {
      if (!selectedProgram) return [];
      const response = await apiClient.get(`/program/${selectedProgram}/weeks`);
      return response.data.data || [];
    },
    enabled: !!selectedProgram,
  });

  const [formData, setFormData] = useState({
    name: "",
    duration_weeks: 4,
    days_per_week: 3,
    periodization_type: "linear",
    description: "",
  });

  const handleCreateProgram = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createProgram.mutateAsync(formData);
      setShowCreateForm(false);
      setFormData({
        name: "",
        duration_weeks: 4,
        days_per_week: 3,
        periodization_type: "linear",
        description: "",
      });
    } catch (error) {
      console.error("Failed to create program:", error);
    }
  };

  const handleScheduleProgram = async (programId: number) => {
    const startDate = prompt("Enter start date (YYYY-MM-DD):");
    if (!startDate) return;

    try {
      await scheduleProgram.mutateAsync({
        programId,
        startDate: new Date(startDate).toISOString(),
      });
      alert("Program scheduled successfully!");
    } catch (error) {
      console.error("Failed to schedule program:", error);
      alert("Failed to schedule program");
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Programs</h2>
          <button
            onClick={() => setShowCreateForm(true)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Create Program
          </button>
        </div>

        {showCreateForm && (
          <div className="mb-6 bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Program</h3>
            <form onSubmit={handleCreateProgram} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Program Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Duration (weeks)</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={formData.duration_weeks}
                    onChange={(e) => setFormData({ ...formData, duration_weeks: parseInt(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Days per Week</label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="7"
                    value={formData.days_per_week}
                    onChange={(e) => setFormData({ ...formData, days_per_week: parseInt(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Periodization</label>
                  <select
                    value={formData.periodization_type}
                    onChange={(e) => setFormData({ ...formData, periodization_type: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="linear">Linear</option>
                    <option value="undulating">Undulating</option>
                    <option value="block">Block</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div className="flex space-x-2">
                <button
                  type="submit"
                  disabled={createProgram.isPending}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
                >
                  {createProgram.isPending ? "Creating..." : "Create Program"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {isLoading ? (
          <div>Loading programs...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {programs.map((program: any) => (
              <div
                key={program.id}
                className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow"
              >
                <h3 className="text-lg font-medium text-gray-900 mb-2">{program.name}</h3>
                <p className="text-sm text-gray-500 mb-4">{program.description || "No description"}</p>
                <div className="space-y-2 mb-4">
                  <div className="text-sm">
                    <span className="font-medium">Duration:</span> {program.duration_weeks} weeks
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Days/Week:</span> {program.days_per_week}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Type:</span> {program.periodization_type}
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setSelectedProgram(program.id)}
                    className="flex-1 px-3 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700"
                  >
                    View Details
                  </button>
                  <button
                    onClick={() => handleScheduleProgram(program.id)}
                    className="flex-1 px-3 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
                  >
                    Schedule
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {programs.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <p className="text-gray-500">No programs yet. Create your first program to get started!</p>
          </div>
        )}

        {/* Program Details Modal */}
        {selectedProgram && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-gray-900">Program Details</h3>
                <button
                  onClick={() => setSelectedProgram(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-4">
                {programWeeks.map((week: any, index: number) => (
                  <div key={week.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="font-medium text-gray-900 mb-2">Week {week.week_number}</div>
                    {week.workout_template_id && (
                      <div className="text-sm text-gray-600">
                        Template: {templates.find((t: any) => t.id === week.workout_template_id)?.name || "Unknown"}
                      </div>
                    )}
                    {week.notes && (
                      <div className="text-sm text-gray-500 mt-2">{week.notes}</div>
                    )}
                  </div>
                ))}
                {programWeeks.length === 0 && (
                  <p className="text-gray-500">No weeks defined for this program.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

