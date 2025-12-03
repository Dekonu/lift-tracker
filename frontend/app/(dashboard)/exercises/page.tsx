"use client";

import { useState, useMemo } from "react";
import { useExercises } from "@/lib/hooks/use-exercises";
import { useMuscleGroups } from "@/lib/hooks/use-muscle-groups";
import { useEquipment } from "@/lib/hooks/use-equipment";

export default function ExercisesPage() {
  const { data: exercises = [], isLoading: exercisesLoading } = useExercises();
  const { data: muscleGroupsData = [], isLoading: muscleGroupsLoading } = useMuscleGroups();
  const { data: equipmentData = [], isLoading: equipmentLoading } = useEquipment();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMuscleGroups, setSelectedMuscleGroups] = useState<number[]>([]);
  const [selectedEquipment, setSelectedEquipment] = useState<number[]>([]);

  // Create a map of muscle group ID to name
  const muscleGroupMap = useMemo(() => {
    const map = new Map<number, string>();
    muscleGroupsData.forEach((mg: any) => {
      map.set(mg.id, mg.name);
    });
    return map;
  }, [muscleGroupsData]);

  // Create a map of equipment ID to name
  const equipmentMap = useMemo(() => {
    const map = new Map<number, string>();
    equipmentData.forEach((eq: any) => {
      map.set(eq.id, eq.name);
    });
    return map;
  }, [equipmentData]);

  // Get unique muscle groups and equipment from exercises
  const muscleGroups = useMemo(() => {
    const groups = new Set<number>();
    exercises.forEach((exercise: any) => {
      exercise.primary_muscle_group_ids?.forEach((id: number) => groups.add(id));
      exercise.secondary_muscle_group_ids?.forEach((id: number) => groups.add(id));
    });
    return Array.from(groups).sort((a, b) => {
      const nameA = muscleGroupMap.get(a) || `Group ${a}`;
      const nameB = muscleGroupMap.get(b) || `Group ${b}`;
      return nameA.localeCompare(nameB);
    });
  }, [exercises, muscleGroupMap]);

  const equipment = useMemo(() => {
    const eq = new Set<number>();
    exercises.forEach((exercise: any) => {
      exercise.equipment_ids?.forEach((id: number) => eq.add(id));
    });
    return Array.from(eq).sort((a, b) => {
      const nameA = equipmentMap.get(a) || `Equipment ${a}`;
      const nameB = equipmentMap.get(b) || `Equipment ${b}`;
      return nameA.localeCompare(nameB);
    });
  }, [exercises, equipmentMap]);

  // Filter exercises
  const filteredExercises = useMemo(() => {
    return exercises.filter((exercise: any) => {
      // Search filter
      if (searchQuery && !exercise.name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }

      // Muscle group filter
      if (selectedMuscleGroups.length > 0) {
        const hasMuscleGroup = selectedMuscleGroups.some(
          (mgId) =>
            exercise.primary_muscle_group_ids?.includes(mgId) ||
            exercise.secondary_muscle_group_ids?.includes(mgId)
        );
        if (!hasMuscleGroup) return false;
      }

      // Equipment filter
      if (selectedEquipment.length > 0) {
        const hasEquipment = selectedEquipment.some((eqId) =>
          exercise.equipment_ids?.includes(eqId)
        );
        if (!hasEquipment) return false;
      }

      // Only show enabled exercises
      return exercise.enabled;
    });
  }, [exercises, searchQuery, selectedMuscleGroups, selectedEquipment]);

  const toggleMuscleGroup = (groupId: number) => {
    setSelectedMuscleGroups((prev) =>
      prev.includes(groupId) ? prev.filter((id) => id !== groupId) : [...prev, groupId]
    );
  };

  const toggleEquipment = (equipmentId: number) => {
    setSelectedEquipment((prev) =>
      prev.includes(equipmentId)
        ? prev.filter((id) => id !== equipmentId)
        : [...prev, equipmentId]
    );
  };

  if (exercisesLoading || muscleGroupsLoading || equipmentLoading) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">Loading exercises...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Exercise Library</h2>

        {/* Search and Filters */}
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search exercises..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-4 py-2"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Muscle Groups
              </label>
              <div className="flex flex-wrap gap-2">
                {muscleGroups.map((mgId) => {
                  const muscleGroupName = muscleGroupMap.get(mgId) || `Group ${mgId}`;
                  return (
                    <button
                      key={mgId}
                      onClick={() => toggleMuscleGroup(mgId)}
                      className={`px-3 py-1 rounded-md text-sm ${
                        selectedMuscleGroups.includes(mgId)
                          ? "bg-indigo-600 text-white"
                          : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                      }`}
                    >
                      {muscleGroupName}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Equipment
              </label>
              <div className="flex flex-wrap gap-2">
                {equipment.map((eqId) => {
                  const equipmentName = equipmentMap.get(eqId) || `Equipment ${eqId}`;
                  return (
                    <button
                      key={eqId}
                      onClick={() => toggleEquipment(eqId)}
                      className={`px-3 py-1 rounded-md text-sm ${
                        selectedEquipment.includes(eqId)
                          ? "bg-indigo-600 text-white"
                          : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                      }`}
                    >
                      {equipmentName}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {(selectedMuscleGroups.length > 0 || selectedEquipment.length > 0) && (
            <div className="mt-4">
              <button
                onClick={() => {
                  setSelectedMuscleGroups([]);
                  setSelectedEquipment([]);
                }}
                className="text-sm text-indigo-600 hover:text-indigo-500"
              >
                Clear filters
              </button>
            </div>
          )}
        </div>

        {/* Exercise List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="text-sm text-gray-500">
              Showing {filteredExercises.length} of {exercises.filter((e: any) => e.enabled).length} exercises
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {filteredExercises.map((exercise: any) => (
              <div key={exercise.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{exercise.name}</h3>
                    {exercise.instructions && (
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {exercise.instructions}
                      </p>
                    )}
                    <div className="flex items-center space-x-4 mt-2">
                      {exercise.primary_muscle_group_names && exercise.primary_muscle_group_names.length > 0 && (
                        <div className="text-xs text-gray-500">
                          Primary: {exercise.primary_muscle_group_names.join(", ")}
                        </div>
                      )}
                      {exercise.equipment_names && exercise.equipment_names.length > 0 && (
                        <div className="text-xs text-gray-500">
                          Equipment: {exercise.equipment_names.join(", ")}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {filteredExercises.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No exercises found matching your filters.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

