-- Migration: Update exercise table to support primary_muscle_group_ids as array and add enabled field
-- This migration:
-- 1. Converts primary_muscle_group_id (single integer) to primary_muscle_group_ids (integer array)
-- 2. Adds enabled boolean field (defaults to true)
-- 3. Removes the foreign key constraint on primary_muscle_group_id (since arrays can't have foreign keys)

-- Step 1: Add new columns
ALTER TABLE exercise 
ADD COLUMN IF NOT EXISTS primary_muscle_group_ids INTEGER[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS enabled BOOLEAN DEFAULT true NOT NULL;

-- Step 2: Migrate existing data - convert single primary_muscle_group_id to array
UPDATE exercise 
SET primary_muscle_group_ids = ARRAY[primary_muscle_group_id]
WHERE primary_muscle_group_id IS NOT NULL;

-- Step 3: Set enabled to true for all existing exercises
UPDATE exercise 
SET enabled = true
WHERE enabled IS NULL;

-- Step 4: Create index on enabled field for faster filtering
CREATE INDEX IF NOT EXISTS idx_exercise_enabled ON exercise(enabled);

-- Step 5: Drop the old primary_muscle_group_id column and its foreign key constraint
-- First, drop the foreign key constraint
ALTER TABLE exercise 
DROP CONSTRAINT IF EXISTS exercise_primary_muscle_group_id_fkey;

-- Then drop the column
ALTER TABLE exercise 
DROP COLUMN IF EXISTS primary_muscle_group_id;

-- Step 6: Drop the old index if it exists
DROP INDEX IF EXISTS idx_exercise_primary_muscle_group;

-- Step 7: Add constraint to ensure at least one primary muscle group (array must not be empty)
ALTER TABLE exercise 
ADD CONSTRAINT exercise_primary_muscle_group_ids_not_empty 
CHECK (array_length(primary_muscle_group_ids, 1) > 0);

-- Note: After running this migration, you may want to verify the data:
-- SELECT id, name, primary_muscle_group_ids, secondary_muscle_group_ids, enabled FROM exercise LIMIT 10;

