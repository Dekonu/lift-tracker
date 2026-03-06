/**
 * Periodization utility functions
 * Generates sets based on periodization type and week number
 */

export type PeriodizationType = "linear" | "undulating" | "block";
export type WeightType = "static" | "percentage" | "rpe" | "rir";

export interface SetConfig {
  id?: number; // For editing existing sets
  set_number: number;
  reps: number | null;
  weight_kg?: number | null;
  percentage_of_1rm?: number | null;
  rpe?: number | null;
  rir?: number | null;
  rest_seconds?: number | null;
  tempo?: string | null;
  notes?: string | null;
  is_warmup?: boolean;
}

export interface ExerciseTemplate {
  exercise_id: number;
  sets: SetConfig[];
  notes?: string;
}

/**
 * Linear Periodization: Progressive increase in intensity, decrease in volume
 */
export function generateLinearSets(
  weekNumber: number,
  totalWeeks: number,
  baseReps: number = 10,
  baseIntensity: number = 65,
  numSets: number = 4
): SetConfig[] {
  // Calculate progression: intensity increases, volume decreases
  const progress = weekNumber / totalWeeks; // 0 to 1
  const intensity = Math.round(baseIntensity + progress * 25); // 65% to 90%
  const reps = Math.max(1, Math.round(baseReps - progress * 7)); // 10 to 3
  const sets = Math.max(2, Math.round(numSets - progress * 2)); // 4 to 2

  return Array.from({ length: sets }, (_, i) => ({
    set_number: i + 1,
    reps,
    percentage_of_1rm: intensity,
    rest_seconds: intensity > 85 ? 300 : 180, // Longer rest for higher intensity
    is_warmup: false,
  }));
}

/**
 * Undulating Periodization: Varies volume and intensity within the week
 */
export function generateUndulatingSets(
  dayOfWeek: number, // 1-7 (Monday = 1, etc.)
  baseReps: number = 8,
  baseIntensity: number = 75
): SetConfig[] {
  // Day 1: High volume, moderate intensity
  // Day 2: Moderate volume, high intensity
  // Day 3: Low volume, very high intensity
  const dayPattern = dayOfWeek % 3;

  let sets: SetConfig[];
  if (dayPattern === 1) {
    // High volume day
    sets = Array.from({ length: 4 }, (_, i) => ({
      set_number: i + 1,
      reps: baseReps + 2, // 10 reps
      percentage_of_1rm: baseIntensity - 5, // 70%
      rest_seconds: 180,
      is_warmup: false,
    }));
  } else if (dayPattern === 2) {
    // Moderate day
    sets = Array.from({ length: 3 }, (_, i) => ({
      set_number: i + 1,
      reps: baseReps, // 8 reps
      percentage_of_1rm: baseIntensity, // 75%
      rest_seconds: 240,
      is_warmup: false,
    }));
  } else {
    // High intensity day
    sets = Array.from({ length: 2 }, (_, i) => ({
      set_number: i + 1,
      reps: baseReps - 5, // 3 reps
      percentage_of_1rm: baseIntensity + 15, // 90%
      rest_seconds: 300,
      is_warmup: false,
    }));
  }

  return sets;
}

/**
 * Block Periodization: Focused training blocks
 */
export function generateBlockSets(
  weekNumber: number,
  totalWeeks: number,
  blockType: "accumulation" | "transmutation" | "realization"
): SetConfig[] {
  const accumulationWeeks = Math.ceil(totalWeeks * 0.5);
  const transmutationWeeks = Math.ceil(totalWeeks * 0.3);
  const realizationWeeks = totalWeeks - accumulationWeeks - transmutationWeeks;

  let sets: SetConfig[];

  if (weekNumber <= accumulationWeeks) {
    // Accumulation: High volume, moderate intensity
    sets = Array.from({ length: 5 }, (_, i) => ({
      set_number: i + 1,
      reps: 8,
      percentage_of_1rm: 70,
      rest_seconds: 180,
      is_warmup: false,
    }));
  } else if (weekNumber <= accumulationWeeks + transmutationWeeks) {
    // Transmutation: Moderate volume/intensity
    sets = Array.from({ length: 4 }, (_, i) => ({
      set_number: i + 1,
      reps: 5,
      percentage_of_1rm: 80,
      rest_seconds: 240,
      is_warmup: false,
    }));
  } else {
    // Realization: Low volume, high intensity
    sets = Array.from({ length: 3 }, (_, i) => ({
      set_number: i + 1,
      reps: 2,
      percentage_of_1rm: 92,
      rest_seconds: 300,
      is_warmup: false,
    }));
  }

  return sets;
}

/**
 * Generate sets based on periodization type
 */
export function generateSetsForPeriodization(
  periodizationType: PeriodizationType,
  weekNumber: number,
  totalWeeks: number,
  dayOfWeek?: number
): SetConfig[] {
  switch (periodizationType) {
    case "linear":
      return generateLinearSets(weekNumber, totalWeeks);
    case "undulating":
      if (!dayOfWeek) {
        // Default to day 1 if not specified
        return generateUndulatingSets(1);
      }
      return generateUndulatingSets(dayOfWeek);
    case "block":
      return generateBlockSets(weekNumber, totalWeeks, "accumulation");
    default:
      // Default: 3 sets of 8 reps at 75%
      return Array.from({ length: 3 }, (_, i) => ({
        set_number: i + 1,
        reps: 8,
        percentage_of_1rm: 75,
        rest_seconds: 180,
        is_warmup: false,
      }));
  }
}

