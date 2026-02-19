-- Migration: Add program_day_assignment table for day-based template scheduling
-- This allows multiple workout templates per day (days 1-7, not tied to calendar)

CREATE TABLE IF NOT EXISTS program_day_assignment (
    id SERIAL PRIMARY KEY,
    program_id INTEGER NOT NULL,
    week_number INTEGER NOT NULL CHECK (week_number > 0),
    day_number INTEGER NOT NULL CHECK (day_number >= 1 AND day_number <= 7),
    workout_template_id INTEGER NOT NULL,
    "order" INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE CASCADE,
    FOREIGN KEY (workout_template_id) REFERENCES workout_template(id) ON DELETE CASCADE,
    UNIQUE(program_id, week_number, day_number, workout_template_id, "order")
);

CREATE INDEX IF NOT EXISTS idx_program_day_assignment_program_id ON program_day_assignment(program_id);
CREATE INDEX IF NOT EXISTS idx_program_day_assignment_workout_template_id ON program_day_assignment(workout_template_id);
CREATE INDEX IF NOT EXISTS idx_program_day_assignment_week_day ON program_day_assignment(program_id, week_number, day_number);

