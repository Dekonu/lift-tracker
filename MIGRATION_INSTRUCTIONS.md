# Database Migration Instructions

To create a migration for the new workout tracking models, run:

```bash
# From the project root
cd src
alembic revision --autogenerate -m "Add workout tracking models"
alembic upgrade head
```

This will automatically generate a migration file that includes:
- `muscle_group` table
- `exercise` table
- `exercise_secondary_muscle_groups` association table
- `workout` table
- `exercise_instance` table
- `set` table

All foreign key relationships and constraints will be automatically detected and included in the migration.

