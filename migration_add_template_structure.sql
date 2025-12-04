-- Migration: Add template exercise and set structure
-- This allows workout templates to store actual exercises and sets

-- Template exercise entries (exercises within a template)
CREATE TABLE IF NOT EXISTS template_exercise_entry (
    id SERIAL PRIMARY KEY,
    workout_template_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    notes VARCHAR(500),
    "order" INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (workout_template_id) REFERENCES workout_template(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercise(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_template_exercise_entry_template_id ON template_exercise_entry(workout_template_id);
CREATE INDEX IF NOT EXISTS idx_template_exercise_entry_exercise_id ON template_exercise_entry(exercise_id);

-- Template set entries (sets within a template exercise)
CREATE TABLE IF NOT EXISTS template_set_entry (
    id SERIAL PRIMARY KEY,
    template_exercise_entry_id INTEGER NOT NULL,
    set_number INTEGER NOT NULL,
    weight_kg DECIMAL(10,2),
    reps INTEGER,
    rir INTEGER CHECK (rir >= 0 AND rir <= 5),  -- Reps in Reserve
    rpe DECIMAL(3,1) CHECK (rpe >= 1.0 AND rpe <= 10.0),  -- Rate of Perceived Exertion
    percentage_of_1rm DECIMAL(5,2) CHECK (percentage_of_1rm > 0 AND percentage_of_1rm <= 100),
    rest_seconds INTEGER CHECK (rest_seconds > 0),
    tempo VARCHAR(20),
    notes VARCHAR(200),
    is_warmup BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (template_exercise_entry_id) REFERENCES template_exercise_entry(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_template_set_entry_exercise_entry_id ON template_set_entry(template_exercise_entry_id);

