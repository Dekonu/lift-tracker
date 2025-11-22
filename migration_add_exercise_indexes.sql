-- Migration script to add database indexes for improved exercise query performance

-- Index on enabled field (used for filtering)
CREATE INDEX IF NOT EXISTS idx_exercise_enabled ON exercise(enabled);

-- Index on name field (used for searching)
CREATE INDEX IF NOT EXISTS idx_exercise_name ON exercise(name);

-- Composite index for common queries (enabled + name)
CREATE INDEX IF NOT EXISTS idx_exercise_enabled_name ON exercise(enabled, name);

-- Index on exercise_equipment for faster JOINs
CREATE INDEX IF NOT EXISTS idx_exercise_equipment_exercise_id ON exercise_equipment(exercise_id);
CREATE INDEX IF NOT EXISTS idx_exercise_equipment_equipment_id ON exercise_equipment(equipment_id);

-- Composite index for equipment filtering (exercise_id + equipment_id)
CREATE INDEX IF NOT EXISTS idx_exercise_equipment_composite ON exercise_equipment(exercise_id, equipment_id);

-- Analyze tables to update statistics
ANALYZE exercise;
ANALYZE exercise_equipment;

