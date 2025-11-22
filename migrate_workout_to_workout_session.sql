-- Migration script to move data from old workout system to new workout_session system
-- Run this after verifying the new system works correctly

-- Step 1: Migrate workouts to workout_sessions
-- Convert workout.date to workout_session.started_at and generate a name
INSERT INTO workout_session (user_id, name, started_at, created_at, updated_at)
SELECT 
    w.user_id,
    'Workout ' || TO_CHAR(w.date, 'YYYY-MM-DD HH24:MI') as name,
    w.date as started_at,
    w.created_at,
    w.updated_at
FROM workout w;

-- Step 2: Create mapping table for workout_id -> workout_session_id
-- This helps us link exercise_instances to exercise_entries
CREATE TEMP TABLE workout_mapping AS
SELECT 
    w.id as old_workout_id,
    ws.id as new_session_id,
    ROW_NUMBER() OVER (PARTITION BY w.user_id, w.date ORDER BY w.id) as rn
FROM workout w
JOIN workout_session ws ON ws.user_id = w.user_id 
    AND ws.started_at = w.date
    AND ws.name LIKE 'Workout ' || TO_CHAR(w.date, 'YYYY-MM-DD%');

-- Step 3: Migrate exercise_instances to exercise_entries
INSERT INTO exercise_entry (workout_session_id, exercise_id, "order", notes, created_at)
SELECT 
    wm.new_session_id as workout_session_id,
    ei.exercise_id,
    ei."order",
    NULL as notes,
    COALESCE(ws.created_at, NOW()) as created_at
FROM exercise_instance ei
JOIN workout_mapping wm ON ei.workout_id = wm.old_workout_id
JOIN workout_session ws ON ws.id = wm.new_session_id;

-- Step 4: Create mapping table for exercise_instance_id -> exercise_entry_id
CREATE TEMP TABLE exercise_entry_mapping AS
SELECT 
    ei.id as old_instance_id,
    ee.id as new_entry_id
FROM exercise_instance ei
JOIN workout_mapping wm ON ei.workout_id = wm.old_workout_id
JOIN exercise_entry ee ON ee.workout_session_id = wm.new_session_id
    AND ee.exercise_id = ei.exercise_id
    AND ee."order" = ei."order";

-- Step 5: Migrate sets to set_entries
-- Convert weight_value + unit to weight_kg
-- Handle percentage type by storing in percentage_of_1rm
INSERT INTO set_entry (
    exercise_entry_id,
    set_number,
    weight_kg,
    reps,
    rir,
    percentage_of_1rm,
    rest_seconds,
    notes,
    is_warmup,
    created_at
)
SELECT 
    eem.new_entry_id as exercise_entry_id,
    ROW_NUMBER() OVER (PARTITION BY s.exercise_instance_id ORDER BY s.id) as set_number,
    CASE 
        WHEN s.unit = 'kg' THEN s.weight_value
        WHEN s.unit = 'lbs' THEN s.weight_value * 0.453592  -- Convert lbs to kg
        ELSE NULL
    END as weight_kg,
    NULL as reps,  -- Old system didn't track reps separately
    s.rir,
    CASE 
        WHEN s.weight_type = 'percentage' THEN s.weight_value
        ELSE NULL
    END as percentage_of_1rm,
    s.rest_time_seconds as rest_seconds,
    s.notes,
    FALSE as is_warmup,
    COALESCE(ee.created_at, NOW()) as created_at
FROM "set" s
JOIN exercise_entry_mapping eem ON s.exercise_instance_id = eem.old_instance_id
JOIN exercise_entry ee ON ee.id = eem.new_entry_id;

-- Step 6: Verify migration
-- Check counts match
SELECT 
    'workout' as old_table, COUNT(*) as count FROM workout
UNION ALL
SELECT 
    'workout_session' as new_table, COUNT(*) as count FROM workout_session
UNION ALL
SELECT 
    'exercise_instance' as old_table, COUNT(*) as count FROM exercise_instance
UNION ALL
SELECT 
    'exercise_entry' as new_table, COUNT(*) as count FROM exercise_entry
UNION ALL
SELECT 
    'set' as old_table, COUNT(*) as count FROM "set"
UNION ALL
SELECT 
    'set_entry' as new_table, COUNT(*) as count FROM set_entry;

-- Note: After verifying the migration, you can:
-- 1. Drop the old tables: DROP TABLE "set" CASCADE; DROP TABLE exercise_instance CASCADE; DROP TABLE workout CASCADE;
-- 2. Remove old API endpoints from the codebase

