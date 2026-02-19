-- Migration: Add User Personal Information Fields and Core Exercise Flag
-- This migration adds:
-- 1. Optional personal information fields to user table (gender, weight, height, birthdate)
-- 2. is_core flag to exercise table to mark core exercises for training programs and LLM suggestions

-- ============================================================================
-- 1. USER PERSONAL INFORMATION FIELDS
-- ============================================================================

-- Handle case where columns might already exist with enum type
-- Convert enum columns to VARCHAR if they exist
-- First, drop any check constraints that reference the enum types (PostgreSQL auto-names them)
DO $$ 
DECLARE
    constraint_name text;
BEGIN
    -- Find and drop net_weight_goal check constraint
    SELECT conname INTO constraint_name
    FROM pg_constraint
    WHERE conrelid = 'user'::regclass
    AND conname LIKE '%net_weight_goal%'
    AND contype = 'c';
    
    IF constraint_name IS NOT NULL THEN
        EXECUTE format('ALTER TABLE "user" DROP CONSTRAINT IF EXISTS %I', constraint_name);
    END IF;
    
    -- Find and drop strength_goal check constraint
    SELECT conname INTO constraint_name
    FROM pg_constraint
    WHERE conrelid = 'user'::regclass
    AND conname LIKE '%strength_goal%'
    AND contype = 'c';
    
    IF constraint_name IS NOT NULL THEN
        EXECUTE format('ALTER TABLE "user" DROP CONSTRAINT IF EXISTS %I', constraint_name);
    END IF;
END $$;

-- Now convert enum columns to VARCHAR
DO $$ 
DECLARE
    col_type text;
BEGIN
    -- Check and convert net_weight_goal column (gender is already VARCHAR)
    SELECT udt_name INTO col_type
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'user' AND column_name = 'net_weight_goal';
    
    IF col_type IS NOT NULL THEN
        IF EXISTS (
            SELECT 1 FROM pg_type t
            WHERE t.typname = col_type AND t.typtype = 'e'
        ) THEN
            -- Convert enum to VARCHAR - cast enum to text explicitly
            EXECUTE format('ALTER TABLE "user" ALTER COLUMN net_weight_goal TYPE VARCHAR(20) USING net_weight_goal::text::VARCHAR(20)');
        END IF;
    END IF;
    
    -- Check and convert strength_goal column to strength_goals array
    -- First, convert enum to VARCHAR if it exists as enum
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'user' AND column_name = 'strength_goal'
    ) THEN
        SELECT udt_name INTO col_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'user' AND column_name = 'strength_goal';
        
        IF col_type IS NOT NULL THEN
            IF EXISTS (
                SELECT 1 FROM pg_type t
                WHERE t.typname = col_type AND t.typtype = 'e'
            ) THEN
                -- Convert enum to VARCHAR first
                EXECUTE format('ALTER TABLE "user" ALTER COLUMN strength_goal TYPE VARCHAR(30) USING strength_goal::text::VARCHAR(30)');
            END IF;
        END IF;
        
        -- Convert single value to array and rename column
        EXECUTE format('ALTER TABLE "user" ALTER COLUMN strength_goal TYPE VARCHAR(30)[] USING CASE WHEN strength_goal IS NULL THEN NULL ELSE ARRAY[strength_goal] END');
        EXECUTE format('ALTER TABLE "user" RENAME COLUMN strength_goal TO strength_goals');
    END IF;
END $$;

-- Add personal information fields to user table
-- Note: Using VARCHAR instead of native enums to avoid type casting issues
ALTER TABLE "user" 
ADD COLUMN IF NOT EXISTS gender VARCHAR(20),
ADD COLUMN IF NOT EXISTS weight_lbs DECIMAL(5,2) CHECK (weight_lbs IS NULL OR weight_lbs > 0),
ADD COLUMN IF NOT EXISTS height_ft INTEGER CHECK (height_ft IS NULL OR (height_ft >= 0 AND height_ft <= 8)),
ADD COLUMN IF NOT EXISTS height_in INTEGER CHECK (height_in IS NULL OR (height_in >= 0 AND height_in < 12)),
ADD COLUMN IF NOT EXISTS birthdate DATE,
ADD COLUMN IF NOT EXISTS net_weight_goal VARCHAR(20),
ADD COLUMN IF NOT EXISTS strength_goals VARCHAR(30)[];

-- Drop existing check constraints if they exist, then add new ones
ALTER TABLE "user" DROP CONSTRAINT IF EXISTS check_gender;
ALTER TABLE "user" DROP CONSTRAINT IF EXISTS check_net_weight_goal;
ALTER TABLE "user" DROP CONSTRAINT IF EXISTS check_strength_goal;
ALTER TABLE "user" DROP CONSTRAINT IF EXISTS user_strength_goal_check;

-- Add check constraints for enum-like validation
ALTER TABLE "user"
ADD CONSTRAINT check_gender CHECK (gender IS NULL OR gender IN ('male', 'female', 'other', 'prefer_not_to_say'));

ALTER TABLE "user"
ADD CONSTRAINT check_net_weight_goal CHECK (net_weight_goal IS NULL OR net_weight_goal IN ('gain', 'lose', 'maintain'));

-- Check constraint for strength_goals array - each element must be a valid strength goal
ALTER TABLE "user"
ADD CONSTRAINT check_strength_goals CHECK (
    strength_goals IS NULL OR 
    (array_length(strength_goals, 1) IS NULL) OR
    (strength_goals <@ ARRAY['overall_health', 'compete', 'personal_milestones', 'bodybuilding', 'powerlifting', 'functional_strength']::VARCHAR(30)[])
);

-- ============================================================================
-- 2. CORE EXERCISE FLAG
-- ============================================================================

-- Add is_core flag to exercise table
ALTER TABLE exercise
ADD COLUMN IF NOT EXISTS is_core BOOLEAN DEFAULT FALSE NOT NULL;

-- Create index for core exercises
CREATE INDEX IF NOT EXISTS idx_exercise_is_core ON exercise(is_core);

-- Mark the specified core exercises as core
-- Note: These exercises should exist in the database. If they don't, you'll need to create them first.
UPDATE exercise 
SET is_core = TRUE 
WHERE name IN (
    'Barbell Squat',
    'Barbell Bench',
    'Deadlift',
    'Weighted Pullup',
    'Weighted Dip',
    'Weighted Muscle up'
);

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. All personal information fields are optional (nullable)
-- 2. Weight is stored in pounds (lbs) as per the UI requirements
-- 3. Height is stored as separate feet and inches fields
-- 4. net_weight_goal: User's weight management goal (gain, lose, maintain)
-- 5. strength_goals: User's strength training objectives (array) - can select multiple:
--    overall_health, compete, personal_milestones, bodybuilding, powerlifting, functional_strength
-- 6. Core exercises are used for training program generation and LLM-based suggestions
-- 7. If the core exercises don't exist yet, create them first before running this migration

