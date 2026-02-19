-- PostgreSQL Database Schema for Lift Tracker
-- Run this SQL in your PostgreSQL database to set up the schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE weight_type AS ENUM ('percentage', 'static');
CREATE TYPE weight_unit AS ENUM ('lbs', 'kg');

-- User table (username removed, email only)
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    profile_image_url VARCHAR DEFAULT 'https://profileimageurl.com',
    uuid UUID UNIQUE DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    tier_id INTEGER
);

-- Create indexes for user table
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
CREATE INDEX IF NOT EXISTS idx_user_is_deleted ON "user"(is_deleted);
CREATE INDEX IF NOT EXISTS idx_user_tier_id ON "user"(tier_id);
CREATE INDEX IF NOT EXISTS idx_user_uuid ON "user"(uuid);

-- Tier table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS tier (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add foreign key constraint for user.tier_id
ALTER TABLE "user" 
ADD CONSTRAINT fk_user_tier 
FOREIGN KEY (tier_id) REFERENCES tier(id);

-- Muscle Group table
CREATE TABLE IF NOT EXISTS muscle_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_muscle_group_name ON muscle_group(name);

-- Exercise table
CREATE TABLE IF NOT EXISTS exercise (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    primary_muscle_group_id INTEGER NOT NULL,
    secondary_muscle_group_ids INTEGER[] DEFAULT '{}',
    FOREIGN KEY (primary_muscle_group_id) REFERENCES muscle_group(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_exercise_name ON exercise(name);
CREATE INDEX IF NOT EXISTS idx_exercise_primary_muscle_group ON exercise(primary_muscle_group_id);

-- Workout table
CREATE TABLE IF NOT EXISTS workout (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_workout_user_id ON workout(user_id);
CREATE INDEX IF NOT EXISTS idx_workout_date ON workout(date);

-- Exercise Instance table
CREATE TABLE IF NOT EXISTS exercise_instance (
    id SERIAL PRIMARY KEY,
    workout_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    "order" INTEGER NOT NULL,
    FOREIGN KEY (workout_id) REFERENCES workout(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercise(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_exercise_instance_workout_id ON exercise_instance(workout_id);
CREATE INDEX IF NOT EXISTS idx_exercise_instance_exercise_id ON exercise_instance(exercise_id);
CREATE INDEX IF NOT EXISTS idx_exercise_instance_order ON exercise_instance("order");

-- Set table
CREATE TABLE IF NOT EXISTS "set" (
    id SERIAL PRIMARY KEY,
    exercise_instance_id INTEGER NOT NULL,
    weight_value DOUBLE PRECISION NOT NULL,
    weight_type weight_type NOT NULL,
    unit weight_unit NOT NULL,
    rest_time_seconds INTEGER,
    rir INTEGER,  -- Reps in Reserve
    notes TEXT,
    FOREIGN KEY (exercise_instance_id) REFERENCES exercise_instance(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_set_exercise_instance_id ON "set"(exercise_instance_id);
CREATE INDEX IF NOT EXISTS idx_set_weight_type ON "set"(weight_type);
CREATE INDEX IF NOT EXISTS idx_set_unit ON "set"(unit);

-- Token blacklist table (for JWT token management)
CREATE TABLE IF NOT EXISTS token_blacklist (
    id SERIAL PRIMARY KEY,
    token VARCHAR NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_token_blacklist_expires_at ON token_blacklist(expires_at);

-- Rate limit table (if needed)
CREATE TABLE IF NOT EXISTS rate_limit (
    id SERIAL PRIMARY KEY,
    tier_id INTEGER NOT NULL,
    path VARCHAR NOT NULL,
    limit_count INTEGER NOT NULL,
    period INTEGER NOT NULL,
    FOREIGN KEY (tier_id) REFERENCES tier(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_tier_id ON rate_limit(tier_id);
CREATE INDEX IF NOT EXISTS idx_rate_limit_path ON rate_limit(path);

-- Post table (if needed for the boilerplate)
CREATE TABLE IF NOT EXISTS post (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    created_by_user_id INTEGER NOT NULL,
    media_url VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (created_by_user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_post_created_by_user_id ON post(created_by_user_id);

-- Optional: Enable Row Level Security (RLS). Policies below use auth.uid() which is
-- Supabase-specific; for standard PostgreSQL, skip this section or define your own policies.
ALTER TABLE "user" ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_instance ENABLE ROW LEVEL SECURITY;
ALTER TABLE "set" ENABLE ROW LEVEL SECURITY;

-- Create policies (users can only see/modify their own data)
-- Note: Adjust these policies based on your security requirements

-- User policies
CREATE POLICY "Users can view their own data" ON "user"
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own data" ON "user"
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Workout policies
CREATE POLICY "Users can view their own workouts" ON workout
    FOR SELECT USING (user_id = (SELECT id FROM "user" WHERE email = auth.jwt() ->> 'email'));

CREATE POLICY "Users can create their own workouts" ON workout
    FOR INSERT WITH CHECK (user_id = (SELECT id FROM "user" WHERE email = auth.jwt() ->> 'email'));

CREATE POLICY "Users can update their own workouts" ON workout
    FOR UPDATE USING (user_id = (SELECT id FROM "user" WHERE email = auth.jwt() ->> 'email'));

CREATE POLICY "Users can delete their own workouts" ON workout
    FOR DELETE USING (user_id = (SELECT id FROM "user" WHERE email = auth.jwt() ->> 'email'));

-- Exercise Instance policies (inherited from workout ownership)
CREATE POLICY "Users can manage exercise instances in their workouts" ON exercise_instance
    FOR ALL USING (
        workout_id IN (
            SELECT id FROM workout WHERE user_id = (SELECT id FROM "user" WHERE email = auth.jwt() ->> 'email')
        )
    );

-- Set policies (inherited from exercise instance ownership)
CREATE POLICY "Users can manage sets in their exercise instances" ON "set"
    FOR ALL USING (
        exercise_instance_id IN (
            SELECT ei.id FROM exercise_instance ei
            JOIN workout w ON ei.workout_id = w.id
            WHERE w.user_id = (SELECT id FROM "user" WHERE email = auth.jwt() ->> 'email')
        )
    );

-- Public read access for exercises and muscle groups (everyone can view)
CREATE POLICY "Anyone can view exercises" ON exercise
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view muscle groups" ON muscle_group
    FOR SELECT USING (true);
