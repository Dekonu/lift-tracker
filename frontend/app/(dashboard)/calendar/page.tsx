"use client";

import { useState, useMemo } from "react";
import { useScheduledWorkouts, useCreateScheduledWorkout, useUpdateScheduledWorkout, useDeleteScheduledWorkout } from "@/lib/hooks/use-scheduled-workouts";
import { useWorkoutTemplates } from "@/lib/hooks/use-programs";
import { useWorkoutSessions } from "@/lib/hooks/use-workouts";
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, startOfWeek, endOfWeek } from "date-fns";

export default function CalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [draggedWorkout, setDraggedWorkout] = useState<number | null>(null);

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);

  const calendarDays = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  // Fetch data
  const { data: scheduledWorkouts = [], isLoading: scheduledLoading } = useScheduledWorkouts(
    calendarStart,
    calendarEnd
  );
  const { data: workoutSessions = [] } = useWorkoutSessions(calendarStart, calendarEnd);
  const { data: templates = [] } = useWorkoutTemplates();
  const createScheduled = useCreateScheduledWorkout();
  const updateScheduled = useUpdateScheduledWorkout();
  const deleteScheduled = useDeleteScheduledWorkout();

  // Group scheduled workouts by date
  const workoutsByDate = useMemo(() => {
    const map = new Map<string, typeof scheduledWorkouts>();
    scheduledWorkouts.forEach((workout: any) => {
      const dateKey = format(new Date(workout.scheduled_date), "yyyy-MM-dd");
      if (!map.has(dateKey)) {
        map.set(dateKey, []);
      }
      map.get(dateKey)!.push(workout);
    });
    return map;
  }, [scheduledWorkouts]);

  // Group completed sessions by date
  const sessionsByDate = useMemo(() => {
    const map = new Map<string, typeof workoutSessions>();
    workoutSessions.forEach((session: any) => {
      const dateKey = format(new Date(session.started_at), "yyyy-MM-dd");
      if (!map.has(dateKey)) {
        map.set(dateKey, []);
      }
      map.get(dateKey)!.push(session);
    });
    return map;
  }, [workoutSessions]);

  const handleDateClick = (date: Date) => {
    setSelectedDate(date);
  };

  const handleDrop = async (date: Date, templateId: number) => {
    if (!templateId) return;

    try {
      await createScheduled.mutateAsync({
        scheduled_date: date.toISOString(),
        workout_template_id: templateId,
      });
    } catch (error) {
      console.error("Failed to schedule workout:", error);
    }
  };

  const handleDragStart = (templateId: number) => {
    setDraggedWorkout(templateId);
  };

  const handleDragEnd = () => {
    setDraggedWorkout(null);
  };

  const getWorkoutsForDate = (date: Date) => {
    const dateKey = format(date, "yyyy-MM-dd");
    const scheduled = workoutsByDate.get(dateKey) || [];
    const completed = sessionsByDate.get(dateKey) || [];
    return { scheduled, completed };
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500";
      case "in_progress":
        return "bg-yellow-500";
      case "skipped":
        return "bg-red-500";
      default:
        return "bg-blue-500";
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Calendar</h2>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentMonth(new Date())}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Today
            </button>
            <button
              onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>

        <div className="grid grid-cols-7 gap-1 mb-6">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
            <div key={day} className="text-center text-sm font-medium text-gray-700 py-2">
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {calendarDays.map((day, dayIdx) => {
            const isCurrentMonth = isSameMonth(day, currentMonth);
            const isToday = isSameDay(day, new Date());
            const isSelected = selectedDate && isSameDay(day, selectedDate);
            const { scheduled, completed } = getWorkoutsForDate(day);

            return (
              <div
                key={day.toISOString()}
                onDragOver={(e) => {
                  e.preventDefault();
                  if (draggedWorkout) {
                    e.currentTarget.classList.add("bg-blue-50");
                  }
                }}
                onDragLeave={(e) => {
                  e.currentTarget.classList.remove("bg-blue-50");
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  e.currentTarget.classList.remove("bg-blue-50");
                  if (draggedWorkout) {
                    handleDrop(day, draggedWorkout);
                  }
                }}
                onClick={() => handleDateClick(day)}
                className={`
                  min-h-[100px] p-2 border border-gray-200 rounded
                  ${!isCurrentMonth ? "bg-gray-50 text-gray-400" : "bg-white"}
                  ${isToday ? "ring-2 ring-indigo-500" : ""}
                  ${isSelected ? "bg-indigo-50" : ""}
                  cursor-pointer hover:bg-gray-50 transition-colors
                `}
              >
                <div className={`text-sm font-medium mb-1 ${isToday ? "text-indigo-600" : ""}`}>
                  {format(day, "d")}
                </div>
                <div className="space-y-1">
                  {scheduled.map((workout: any) => (
                    <div
                      key={workout.id}
                      className={`text-xs px-1 py-0.5 rounded ${getStatusColor(workout.status)} text-white truncate`}
                      title={workout.workout_template?.name || "Workout"}
                    >
                      {workout.workout_template?.name || "Workout"}
                    </div>
                  ))}
                  {completed.map((session: any) => (
                    <div
                      key={session.id}
                      className="text-xs px-1 py-0.5 rounded bg-green-500 text-white truncate"
                      title={session.name || "Completed"}
                    >
                      ✓ {session.name || "Completed"}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Template Library Sidebar */}
        <div className="mt-8 bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Workout Templates</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {templates.map((template: any) => (
              <div
                key={template.id}
                draggable
                onDragStart={() => handleDragStart(template.id)}
                onDragEnd={handleDragEnd}
                className="p-4 border border-gray-300 rounded-lg cursor-move hover:bg-gray-50 hover:shadow-md transition-shadow"
              >
                <div className="font-medium text-sm text-gray-900">{template.name}</div>
                {template.description && (
                  <div className="text-xs text-gray-500 mt-1">{template.description}</div>
                )}
              </div>
            ))}
          </div>
          {templates.length === 0 && (
            <p className="text-sm text-gray-500">No workout templates available. Create one to start scheduling workouts.</p>
          )}
        </div>

        {/* Selected Date Details */}
        {selectedDate && (
          <div className="mt-8 bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {format(selectedDate, "EEEE, MMMM d, yyyy")}
            </h3>
            <div className="space-y-4">
              {getWorkoutsForDate(selectedDate).scheduled.map((workout: any) => (
                <div key={workout.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">
                      {workout.workout_template?.name || "Workout"}
                    </div>
                    <div className="text-sm text-gray-500">Status: {workout.status}</div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => updateScheduled.mutate({ id: workout.id, data: { status: "completed" } })}
                      className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
                    >
                      Complete
                    </button>
                    <button
                      onClick={() => deleteScheduled.mutate(workout.id)}
                      className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
              {getWorkoutsForDate(selectedDate).scheduled.length === 0 && (
                <p className="text-sm text-gray-500">No workouts scheduled for this date.</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

