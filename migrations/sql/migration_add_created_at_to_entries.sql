-- Migration script to add created_at columns to exercise_entry and set_entry tables
-- for audit purposes

-- Add created_at to exercise_entry
ALTER TABLE exercise_entry 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL;

-- Add created_at to set_entry
ALTER TABLE set_entry 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL;

-- Update existing records to have created_at set to a reasonable default
-- Use the workout_session's created_at as a fallback for exercise_entry
UPDATE exercise_entry 
SET created_at = (
    SELECT ws.created_at 
    FROM workout_session ws 
    WHERE ws.id = exercise_entry.workout_session_id
)
WHERE created_at IS NULL;

-- Use the exercise_entry's created_at as a fallback for set_entry
UPDATE set_entry 
SET created_at = (
    SELECT ee.created_at 
    FROM exercise_entry ee 
    WHERE ee.id = set_entry.exercise_entry_id
)
WHERE created_at IS NULL;

-- If still NULL (shouldn't happen, but just in case), use current timestamp
UPDATE exercise_entry SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;
UPDATE set_entry SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;

