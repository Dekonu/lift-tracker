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

  const [scheduleDate, setScheduleDate] = useState<string>("");
  const [schedulingProgramId, setSchedulingProgramId] = useState<number | null>(null);

  const handleScheduleProgram = async (programId: number) => {
    setSchedulingProgramId(programId);
    // Set default date to today
    const today = new Date().toISOString().split("T")[0];
    setScheduleDate(today);
  };

  const confirmSchedule = async () => {
    if (!schedulingProgramId || !scheduleDate) return;

    try {
      // Convert date to ISO datetime string (start of day)
      const startDate = new Date(scheduleDate + "T00:00:00").toISOString();
      await scheduleProgram.mutateAsync({
        programId: schedulingProgramId,
        startDate,
      });
      setSchedulingProgramId(null);
      setScheduleDate("");
      alert("Program scheduled successfully!");
    } catch (error: any) {
      console.error("Failed to schedule program:", error);
      alert(error?.response?.data?.detail || "Failed to schedule program");
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
      <div className="px-4 sm:px-0">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <h1 className="text-3xl font-bold text-neutral-900">Programs</h1>
            <button
              onClick={() => setShowCreateForm(true)}
              className="btn-primary"
            >
              Create Program
            </button>
          </div>
          <p className="text-neutral-600">Create and manage your training programs.</p>
        </div>

        {showCreateForm && (
          <div className="mb-8 card p-6">
            <h3 className="text-xl font-semibold text-neutral-900 mb-4">Create New Program</h3>
            <form onSubmit={handleCreateProgram} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Program Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 12-Week Strength Program"
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">Duration (weeks)</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={formData.duration_weeks}
                    onChange={(e) => setFormData({ ...formData, duration_weeks: parseInt(e.target.value) })}
                    className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">Days per Week</label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="7"
                    value={formData.days_per_week}
                    onChange={(e) => setFormData({ ...formData, days_per_week: parseInt(e.target.value) })}
                    className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">Periodization</label>
                  <select
                    value={formData.periodization_type}
                    onChange={(e) => setFormData({ ...formData, periodization_type: e.target.value })}
                    className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="linear">Linear</option>
                    <option value="undulating">Undulating</option>
                    <option value="block">Block</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Describe your program..."
                />
              </div>
              <div className="flex space-x-2">
                <button
                  type="submit"
                  disabled={createProgram.isPending}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createProgram.isPending ? "Creating..." : "Create Program"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <>
            {programs.length === 0 ? (
              <div className="text-center py-12 card">
                <p className="text-neutral-600">No programs yet. Create your first program to get started!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {programs.map((program: any) => (
                  <div
                    key={program.id}
                    className="card p-6"
                  >
                    <h3 className="text-lg font-semibold text-neutral-900 mb-2">{program.name}</h3>
                    <p className="text-sm text-neutral-600 mb-4">{program.description || "No description"}</p>
                    <div className="space-y-2 mb-4">
                      <div className="text-sm">
                        <span className="font-medium text-neutral-700">Duration:</span>{" "}
                        <span className="text-neutral-600">{program.duration_weeks} weeks</span>
                      </div>
                      <div className="text-sm">
                        <span className="font-medium text-neutral-700">Days/Week:</span>{" "}
                        <span className="text-neutral-600">{program.days_per_week}</span>
                      </div>
                      <div className="text-sm">
                        <span className="font-medium text-neutral-700">Type:</span>{" "}
                        <span className="text-neutral-600 capitalize">{program.periodization_type}</span>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setSelectedProgram(program.id)}
                        className="flex-1 btn-secondary text-sm"
                      >
                        View Details
                      </button>
                      <button
                        onClick={() => handleScheduleProgram(program.id)}
                        className="flex-1 btn-primary text-sm"
                      >
                        Schedule
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* Schedule Program Modal */}
        {schedulingProgramId && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 max-w-md w-full shadow-strong">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-neutral-900">Schedule Program</h3>
                <button
                  onClick={() => {
                    setSchedulingProgramId(null);
                    setScheduleDate("");
                  }}
                  className="text-neutral-500 hover:text-neutral-700 text-2xl leading-none"
                  aria-label="Close"
                >
                  ×
                </button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={scheduleDate}
                    onChange={(e) => setScheduleDate(e.target.value)}
                    className="w-full border border-neutral-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                  />
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={confirmSchedule}
                    disabled={scheduleProgram.isPending || !scheduleDate}
                    className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {scheduleProgram.isPending ? "Scheduling..." : "Schedule"}
                  </button>
                  <button
                    onClick={() => {
                      setSchedulingProgramId(null);
                      setScheduleDate("");
                    }}
                    className="flex-1 btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Program Details Modal */}
        {selectedProgram && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto shadow-strong">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold text-neutral-900">Program Details</h3>
                <button
                  onClick={() => setSelectedProgram(null)}
                  className="text-neutral-500 hover:text-neutral-700 text-2xl leading-none"
                  aria-label="Close"
                >
                  ×
                </button>
              </div>
              <div className="space-y-4">
                {programWeeks.length === 0 ? (
                  <p className="text-neutral-500 text-center py-8">No weeks defined for this program.</p>
                ) : (
                  programWeeks.map((week: any, index: number) => (
                    <div key={week.id} className="card p-4">
                      <div className="font-semibold text-neutral-900 mb-2">Week {week.week_number}</div>
                      {week.workout_template_id && (
                        <div className="text-sm text-neutral-600 mb-1">
                          <span className="font-medium">Template:</span>{" "}
                          {templates.find((t: any) => t.id === week.workout_template_id)?.name || "Unknown"}
                        </div>
                      )}
                      {week.notes && (
                        <div className="text-sm text-neutral-500 mt-2">{week.notes}</div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

