-- Migration: Add scheduled_workout table
-- This table bridges programs and actual workout sessions, allowing users to schedule workouts

CREATE TABLE IF NOT EXISTS scheduled_workout (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    workout_template_id INTEGER NOT NULL REFERENCES workout_template(id) ON DELETE CASCADE,
    scheduled_date TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Program context
    program_id INTEGER REFERENCES program(id) ON DELETE SET NULL,
    program_week INTEGER,
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',  -- scheduled, completed, skipped, in_progress
    completed_workout_session_id INTEGER REFERENCES workout_session(id) ON DELETE SET NULL,
    
    -- User customization
    notes VARCHAR(500),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT scheduled_workout_status_check CHECK (status IN ('scheduled', 'completed', 'skipped', 'in_progress'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_scheduled_workout_user_id ON scheduled_workout(user_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_workout_template_id ON scheduled_workout(workout_template_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_workout_scheduled_date ON scheduled_workout(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_scheduled_workout_program_id ON scheduled_workout(program_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_workout_status ON scheduled_workout(status);
CREATE INDEX IF NOT EXISTS idx_scheduled_workout_completed_session ON scheduled_workout(completed_workout_session_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_workout_user_date ON scheduled_workout(user_id, scheduled_date);

-- Add comment
COMMENT ON TABLE scheduled_workout IS 'Planned workouts assigned to specific dates, can be part of a program or standalone';

