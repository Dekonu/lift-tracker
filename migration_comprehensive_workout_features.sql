-- Comprehensive Migration: Workout Tracking, Analytics, and Social Features
-- This migration adds all the infrastructure for:
-- 1. User profiles with goals and preferences
-- 2. Equipment and exercise enhancements
-- 3. Workout structure (templates, sessions, entries, sets)
-- 4. 1RM tracking
-- 5. Programs and periodization
-- 6. Social features (relationships, sharing)
-- 7. Analytics (volume tracking, strength progression)

-- ============================================================================
-- 1. USER PROFILE
-- ============================================================================

-- Create enum types for user profile
CREATE TYPE goal_type AS ENUM ('gain_strength', 'gain_muscle', 'lose_weight', 'maintain', 'improve_endurance', 'sport_specific');
CREATE TYPE experience_level_type AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE training_style_type AS ENUM ('powerlifting', 'bodybuilding', 'general_fitness', 'calisthenics', 'crossfit');

CREATE TABLE IF NOT EXISTS user_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    goal goal_type NOT NULL,
    experience_level experience_level_type NOT NULL,
    training_style training_style_type,
    training_frequency_days_per_week INTEGER CHECK (training_frequency_days_per_week > 0 AND training_frequency_days_per_week <= 7),
    preferred_workout_duration_minutes INTEGER CHECK (preferred_workout_duration_minutes > 0),
    current_weight_kg DECIMAL(5,2) CHECK (current_weight_kg > 0),
    target_weight_kg DECIMAL(5,2) CHECK (target_weight_kg > 0),
    target_date TIMESTAMP WITH TIME ZONE,
    notes VARCHAR(1000),
    injury_limitations VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_profile_user_id ON user_profile(user_id);

-- ============================================================================
-- 2. EQUIPMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS equipment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200)
);

CREATE INDEX IF NOT EXISTS idx_equipment_name ON equipment(name);

-- Many-to-many relationship between exercises and equipment
CREATE TABLE IF NOT EXISTS exercise_equipment (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL,
    equipment_id INTEGER NOT NULL,
    FOREIGN KEY (exercise_id) REFERENCES exercise(id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
    UNIQUE(exercise_id, equipment_id)
);

CREATE INDEX IF NOT EXISTS idx_exercise_equipment_exercise_id ON exercise_equipment(exercise_id);
CREATE INDEX IF NOT EXISTS idx_exercise_equipment_equipment_id ON exercise_equipment(equipment_id);

-- ============================================================================
-- 3. EXERCISE ENHANCEMENTS
-- ============================================================================

-- Exercise categories
CREATE TABLE IF NOT EXISTS exercise_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200)
);

CREATE INDEX IF NOT EXISTS idx_exercise_category_name ON exercise_category(name);

-- Add category and metadata columns to exercise table
ALTER TABLE exercise 
ADD COLUMN IF NOT EXISTS category_id INTEGER,
ADD COLUMN IF NOT EXISTS instructions VARCHAR(2000),
ADD COLUMN IF NOT EXISTS common_mistakes VARCHAR(1000);

ALTER TABLE exercise
ADD CONSTRAINT fk_exercise_category FOREIGN KEY (category_id) REFERENCES exercise_category(id);

CREATE INDEX IF NOT EXISTS idx_exercise_category_id ON exercise(category_id);

-- Exercise variations (progressions/regressions)
CREATE TABLE IF NOT EXISTS exercise_variation (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL,
    variation_exercise_id INTEGER NOT NULL,
    variation_type VARCHAR(20) NOT NULL CHECK (variation_type IN ('easier', 'harder', 'alternative')),
    notes VARCHAR(200),
    FOREIGN KEY (exercise_id) REFERENCES exercise(id) ON DELETE CASCADE,
    FOREIGN KEY (variation_exercise_id) REFERENCES exercise(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_exercise_variation_exercise_id ON exercise_variation(exercise_id);
CREATE INDEX IF NOT EXISTS idx_exercise_variation_variation_exercise_id ON exercise_variation(variation_exercise_id);

-- ============================================================================
-- 4. WORKOUT STRUCTURE
-- ============================================================================

-- Workout templates (reusable workout structures)
CREATE TABLE IF NOT EXISTS workout_template (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    is_public BOOLEAN DEFAULT FALSE NOT NULL,
    estimated_duration_minutes INTEGER CHECK (estimated_duration_minutes > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_workout_template_user_id ON workout_template(user_id);
CREATE INDEX IF NOT EXISTS idx_workout_template_is_public ON workout_template(is_public);

-- Workout sessions (actual logged workouts)
CREATE TABLE IF NOT EXISTS workout_session (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    workout_template_id INTEGER,
    name VARCHAR(100) NOT NULL,
    notes VARCHAR(1000),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER CHECK (duration_minutes > 0),
    total_volume_kg DECIMAL(10,2),
    total_sets INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (workout_template_id) REFERENCES workout_template(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_workout_session_user_id ON workout_session(user_id);
CREATE INDEX IF NOT EXISTS idx_workout_session_started_at ON workout_session(started_at);
CREATE INDEX IF NOT EXISTS idx_workout_session_workout_template_id ON workout_session(workout_template_id);

-- Exercise entries within a workout session
CREATE TABLE IF NOT EXISTS exercise_entry (
    id SERIAL PRIMARY KEY,
    workout_session_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    notes VARCHAR(500),
    "order" INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (workout_session_id) REFERENCES workout_session(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercise(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_exercise_entry_workout_session_id ON exercise_entry(workout_session_id);
CREATE INDEX IF NOT EXISTS idx_exercise_entry_exercise_id ON exercise_entry(exercise_id);

-- Set entries (individual sets within an exercise entry)
CREATE TABLE IF NOT EXISTS set_entry (
    id SERIAL PRIMARY KEY,
    exercise_entry_id INTEGER NOT NULL,
    set_number INTEGER NOT NULL CHECK (set_number > 0),
    weight_kg DECIMAL(8,2) CHECK (weight_kg > 0),
    reps INTEGER CHECK (reps > 0),
    rir INTEGER CHECK (rir >= 0 AND rir <= 5),  -- Reps in Reserve
    rpe DECIMAL(3,1) CHECK (rpe >= 1.0 AND rpe <= 10.0),  -- Rate of Perceived Exertion
    percentage_of_1rm DECIMAL(5,2) CHECK (percentage_of_1rm > 0 AND percentage_of_1rm <= 100),
    rest_seconds INTEGER CHECK (rest_seconds > 0),
    tempo VARCHAR(20),  -- e.g., "3-1-1-0"
    notes VARCHAR(200),
    is_warmup BOOLEAN DEFAULT FALSE NOT NULL,
    FOREIGN KEY (exercise_entry_id) REFERENCES exercise_entry(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_set_entry_exercise_entry_id ON set_entry(exercise_entry_id);

-- ============================================================================
-- 5. 1RM TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS one_rm (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    weight_kg DECIMAL(8,2) NOT NULL CHECK (weight_kg > 0),
    is_estimated BOOLEAN DEFAULT TRUE NOT NULL,
    tested_date TIMESTAMP WITH TIME ZONE,
    calculation_method VARCHAR(50),  -- 'epley', 'brzycki', etc.
    based_on_weight DECIMAL(8,2) CHECK (based_on_weight > 0),
    based_on_reps INTEGER CHECK (based_on_reps > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercise(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_one_rm_user_id ON one_rm(user_id);
CREATE INDEX IF NOT EXISTS idx_one_rm_exercise_id ON one_rm(exercise_id);
CREATE INDEX IF NOT EXISTS idx_one_rm_user_exercise ON one_rm(user_id, exercise_id);

-- ============================================================================
-- 6. PROGRAMS AND PERIODIZATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS program (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(1000),
    duration_weeks INTEGER NOT NULL CHECK (duration_weeks > 0),
    days_per_week INTEGER NOT NULL CHECK (days_per_week > 0 AND days_per_week <= 7),
    periodization_type VARCHAR(50) NOT NULL,  -- 'linear', 'undulating', 'block', etc.
    is_public BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_program_user_id ON program(user_id);
CREATE INDEX IF NOT EXISTS idx_program_is_public ON program(is_public);
CREATE INDEX IF NOT EXISTS idx_program_is_active ON program(is_active);

-- Program weeks (for periodization)
CREATE TABLE IF NOT EXISTS program_week (
    id SERIAL PRIMARY KEY,
    program_id INTEGER NOT NULL,
    week_number INTEGER NOT NULL CHECK (week_number > 0),
    volume_modifier DECIMAL(4,2) CHECK (volume_modifier > 0 AND volume_modifier <= 2.0),
    intensity_modifier DECIMAL(4,2) CHECK (intensity_modifier > 0 AND intensity_modifier <= 2.0),
    notes VARCHAR(500),
    workout_template_id INTEGER,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE,
    FOREIGN KEY (workout_template_id) REFERENCES workout_template(id) ON DELETE SET NULL,
    UNIQUE(program_id, week_number)
);

CREATE INDEX IF NOT EXISTS idx_program_week_program_id ON program_week(program_id);
CREATE INDEX IF NOT EXISTS idx_program_week_workout_template_id ON program_week(workout_template_id);

-- ============================================================================
-- 7. SOCIAL FEATURES
-- ============================================================================

-- User relationships
CREATE TYPE relationship_type AS ENUM ('follow', 'friend', 'block');

CREATE TABLE IF NOT EXISTS user_relationship (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    related_user_id INTEGER NOT NULL,
    relationship_type relationship_type NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (related_user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    UNIQUE(user_id, related_user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_relationship_user_id ON user_relationship(user_id);
CREATE INDEX IF NOT EXISTS idx_user_relationship_related_user_id ON user_relationship(related_user_id);
CREATE INDEX IF NOT EXISTS idx_user_relationship_type ON user_relationship(relationship_type);

-- Sharing permissions
CREATE TYPE shareable_resource_type AS ENUM ('workout_template', 'program', 'workout_session');

CREATE TABLE IF NOT EXISTS sharing_permission (
    id SERIAL PRIMARY KEY,
    resource_type shareable_resource_type NOT NULL,
    resource_id INTEGER NOT NULL,
    owner_user_id INTEGER NOT NULL,
    shared_with_user_id INTEGER,  -- NULL = public
    can_view BOOLEAN DEFAULT TRUE NOT NULL,
    can_edit BOOLEAN DEFAULT FALSE NOT NULL,
    can_copy BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (owner_user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_with_user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sharing_permission_resource ON sharing_permission(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_sharing_permission_owner ON sharing_permission(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_sharing_permission_shared_with ON sharing_permission(shared_with_user_id);

-- ============================================================================
-- 8. ANALYTICS
-- ============================================================================

-- Volume tracking per muscle group per time period
CREATE TABLE IF NOT EXISTS volume_tracking (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    muscle_group_id INTEGER NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    period_type VARCHAR(20) NOT NULL,  -- 'week', 'month', 'year'
    total_volume_kg DECIMAL(12,2) NOT NULL CHECK (total_volume_kg >= 0),
    total_sets INTEGER NOT NULL CHECK (total_sets >= 0),
    total_reps INTEGER NOT NULL CHECK (total_reps >= 0),
    average_intensity DECIMAL(5,2) CHECK (average_intensity >= 0 AND average_intensity <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (muscle_group_id) REFERENCES muscle_group(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_volume_tracking_user_id ON volume_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_volume_tracking_muscle_group_id ON volume_tracking(muscle_group_id);
CREATE INDEX IF NOT EXISTS idx_volume_tracking_period ON volume_tracking(period_start, period_end);

-- Strength progression tracking
CREATE TABLE IF NOT EXISTS strength_progression (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    estimated_1rm_kg DECIMAL(8,2) NOT NULL CHECK (estimated_1rm_kg > 0),
    volume_kg DECIMAL(10,2) NOT NULL CHECK (volume_kg >= 0),
    average_rpe DECIMAL(3,1) CHECK (average_rpe >= 1.0 AND average_rpe <= 10.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercise(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_strength_progression_user_id ON strength_progression(user_id);
CREATE INDEX IF NOT EXISTS idx_strength_progression_exercise_id ON strength_progression(exercise_id);
CREATE INDEX IF NOT EXISTS idx_strength_progression_date ON strength_progression(date);
CREATE INDEX IF NOT EXISTS idx_strength_progression_user_exercise_date ON strength_progression(user_id, exercise_id, date);

-- ============================================================================
-- NOTES
-- ============================================================================
-- This migration creates the infrastructure for:
-- - User profiles with goals and training preferences
-- - Equipment management and exercise enhancements
-- - Complete workout logging (templates, sessions, entries, sets)
-- - 1RM tracking with estimation methods
-- - Multi-week programs with periodization support
-- - Social features (relationships, sharing permissions)
-- - Analytics (volume tracking, strength progression)
--
-- Deferred features (to be implemented later):
-- - LLM integration endpoints for workout generation
-- - Calendar UI for workout scheduling
-- - Social UI for following/sharing workouts
-- - Advanced analytics dashboards
-- ============================================================================

