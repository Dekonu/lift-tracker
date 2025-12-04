# Program Template Feature - Implementation Summary

## Overview
This feature enables users to create workout templates with exercises and sets, then assign them to program weeks for structured periodized training.

## What Was Built

### Backend

1. **Database Models**:
   - `TemplateExerciseEntry` - Stores exercises within a template
   - `TemplateSetEntry` - Stores sets for each exercise
   - Updated `WorkoutTemplate` - Now has relationship to template exercises

2. **Schemas**:
   - `TemplateExerciseEntryCreate/Read/Update`
   - `TemplateSetEntryCreate/Read/Update`
   - Updated `WorkoutTemplateCreate/Read` to include nested exercises

3. **API Endpoints**:
   - `POST /workout-template` - Create template with exercises and sets
   - `GET /workout-template/{id}` - Get template with full structure
   - `GET /workout-templates` - List templates with exercises
   - `PATCH /program/{id}/week/{week_id}` - Update program week assignment

4. **CRUD Operations**:
   - `crud_template_exercise_entry`
   - `crud_template_set_entry`

### Frontend

1. **Periodization Utilities** (`lib/utils/periodization.ts`):
   - `generateLinearSets()` - Progressive intensity/volume changes
   - `generateUndulatingSets()` - Weekly variation patterns
   - `generateBlockSets()` - Block periodization phases
   - Helper functions for all periodization types

2. **Template Builder Component** (`components/TemplateBuilder.tsx`):
   - Create workout templates with exercises
   - Add/remove exercises dynamically
   - Add/remove sets per exercise
   - Support for static weights or percentage of 1RM
   - Auto-generate sets based on periodization type
   - Modern, card-based UI

3. **Program Week Editor** (`components/ProgramWeekEditor.tsx`):
   - Visual grid showing all program weeks
   - Assign templates to weeks via dropdown
   - Create new templates inline
   - Periodization information display
   - Real-time updates

4. **Updated Programs Page**:
   - "Edit Weeks" button on each program card
   - Opens ProgramWeekEditor modal
   - Seamless integration with existing flow

## Periodization Types Explained

### Linear Periodization
- **Concept**: Progressive increase in intensity, decrease in volume
- **Example**: Week 1-4: 4×10 @ 65%, Week 5-8: 3×6 @ 80%, Week 9-12: 2×3 @ 90%
- **Best For**: Beginners, general strength building

### Undulating Periodization (DUP)
- **Concept**: Varies volume/intensity within the week
- **Example**: Mon: 4×10 @ 70%, Wed: 3×5 @ 85%, Fri: 2×3 @ 90%
- **Best For**: Intermediate/advanced, 3+ days/week

### Block Periodization
- **Concept**: Focused training blocks (mesocycles)
- **Example**: Weeks 1-6: Accumulation (5×8 @ 70%), Weeks 7-10: Transmutation (4×5 @ 80%), Weeks 11-13: Realization (3×2 @ 92%)
- **Best For**: Advanced athletes, competition prep

## How to Use

### Creating a Template

1. Click "Edit Weeks" on any program
2. Click "+ New Template" button
3. Fill in template name and description
4. Select weight type (Percentage or Static)
5. Add exercises:
   - Select from dropdown
   - Sets are auto-generated based on periodization type
   - Customize reps, weight/%, rest time
   - Add/remove sets as needed
6. Click "Create Template"

### Assigning Templates to Weeks

1. In Program Week Editor, see grid of all weeks
2. For each week, select a template from dropdown
3. Templates are automatically saved
4. Can create new templates inline without leaving the editor

### Weight Specification

**Percentage of 1RM**:
- Enter percentage (e.g., 75 for 75% of 1RM)
- Automatically calculates weight when template is used
- Adjusts if user's 1RM changes

**Static Weight**:
- Enter fixed weight in kg
- Same weight for all sets
- Useful for bodyweight or fixed-load exercises

## Database Migration

Run the migration to create the new tables:

```sql
-- See migration_add_template_structure.sql
```

This creates:
- `template_exercise_entry` table
- `template_set_entry` table
- Proper indexes and foreign keys

## Next Steps / Future Enhancements

1. **Template Preview**: Show template structure before creating
2. **Template Library**: Browse and copy public templates
3. **Periodization Visualization**: Charts showing intensity/volume progression
4. **Template Variations**: Create variations of existing templates
5. **Auto-progression**: Automatically adjust weights based on performance
6. **RPE/RIR Support**: Add RPE/RIR-based weight selection in UI
7. **Template Export/Import**: Share templates via JSON

## Technical Notes

- Templates support nested creation (template → exercises → sets) in single API call
- All relationships use proper cascade deletes
- Frontend uses React Query for efficient data fetching
- Periodization helpers can be extended for custom patterns
- UI is fully responsive and mobile-friendly

