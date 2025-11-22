# Database Redundancy Analysis

## Current Situation

There are **two parallel systems** for tracking workouts, which creates redundancy:

### Old System (Currently in Use)
- **`workout`** table: Simple workout with just `date` and `user_id`
- **`exercise_instance`** table: Links workout to exercise with `order`
- **`set`** table: Basic set tracking with:
  - `weight_value`, `weight_type` (percentage/static), `unit` (lbs/kg)
  - `rest_time_seconds`, `rir`, `notes`

**API Endpoints:** `/v1/workout`, `/v1/workout/{id}/exercise-instance`, `/v1/exercise-instance/{id}/set`

### New System (From Comprehensive Migration - Not Currently Used)
- **`workout_session`** table: Feature-rich workout session with:
  - `name`, `started_at`, `completed_at`, `duration_minutes`
  - `workout_template_id` (for reusable templates)
  - `notes`, `total_volume_kg`, `total_sets` (calculated metrics)
- **`exercise_entry`** table: Exercise entry within a workout session
- **`set_entry`** table: Advanced set tracking with:
  - `weight_kg`, `reps`, `set_number`
  - `rir`, `rpe` (Rate of Perceived Exertion)
  - `percentage_of_1rm`, `rest_seconds`, `tempo`
  - `notes`, `is_warmup`

**API Endpoints:** `/v1/workout-session`, `/v1/workout-session/{id}/exercise-entry`, `/v1/exercise-entry/{id}/set`

## Recommendation

**Consolidate to use `workout_session` system** because:
1. ✅ More feature-rich (supports advanced metrics, templates, calculated totals)
2. ✅ Aligns with the comprehensive migration that was completed
3. ✅ Supports future features (periodization, analytics, social sharing)
4. ✅ Better data model for tracking progression

## Migration Path

1. **Update frontend** to use `/v1/workout-session` endpoints instead of `/v1/workout`
2. **Migrate existing data** from `workout` → `workout_session`, `exercise_instance` → `exercise_entry`, `set` → `set_entry`
3. **Deprecate old endpoints** (or keep as legacy support)
4. **Drop old tables** after migration is complete

## Action Items

- [ ] Fix immediate bug: Missing `db.commit()` in exercise instance and set creation
- [ ] Update frontend to use WorkoutSession API
- [ ] Create data migration script
- [ ] Test migration with existing data
- [ ] Remove old tables and endpoints

