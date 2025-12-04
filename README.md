<h1 align="center">Lift Tracker</h1>
<p align="center" markdown=1>
  <i>A comprehensive workout tracking API built with FastAPI</i>
</p>

<p align="center">
  <a href="https://fastapi.tiangolo.com">
      <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  </a>
  <a href="https://docs.pydantic.dev/2.4/">
      <img src="https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=fff&style=for-the-badge" alt="Pydantic">
  </a>
  <a href="https://www.postgresql.org">
      <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  </a>
  <a href="https://redis.io">
      <img src="https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=fff&style=for-the-badge" alt="Redis">
  </a>
  <a href="https://docs.docker.com/compose/">
      <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff&style=for-the-badge" alt="Docker">
  </a>
  <a href="https://wger.de/api/v2/">
      <img src="https://img.shields.io/badge/Wger_API-4CAF50?style=for-the-badge&logo=api&logoColor=white" alt="Wger API">
  </a>
</p>

---

## 🚧 Future Enhancements

The following features have infrastructure in place but require UI/API implementation:

### LLM Integration
- **Status**: Database models and schemas ready
- **To Implement**: 
  - API endpoints for LLM-powered workout generation
  - Integration with LLM services (OpenAI, Anthropic, etc.)
  - Context-aware exercise selection based on user profile
  - Smart progression suggestions

### Calendar UI
- **Status**: Workout sessions support date/time tracking
- **To Implement**:
  - Calendar view for scheduling workouts
  - Drag-and-drop workout assignment
  - Program application to calendar dates
  - Planned vs. actual workout comparison

### Social Features UI
- **Status**: User relationships and sharing permissions models ready
- **To Implement**:
  - Follow/unfollow users interface
  - Share workout templates and programs
  - Public workout feed
  - Social workout challenges

### Advanced Analytics Dashboard
- **Status**: Volume tracking and strength progression models ready
- **To Implement**:
  - Volume progression charts
  - Strength progression graphs
  - Muscle group balance visualization
  - Training frequency analytics
  - Plateau detection and alerts

---

## 📖 About

**Lift Tracker** is a comprehensive exercise and workout tracking application that enables users to create detailed training sessions by combining exercises and sets. The application integrates with the [Wger API](https://wger.de/api/v2/) to provide an extensive exercise database, making it easy to build and track personalized workout routines.

### Infrastructure Status

The application includes comprehensive infrastructure for advanced features:

✅ **Implemented:**
- User profiles with goals, experience levels, and training preferences
- Equipment management and exercise enhancements (categories, variations)
- Complete workout structure (templates, sessions, entries, sets)
- Advanced set tracking (RIR/RPE, percentages, tempo, rest periods)
- 1RM tracking with estimation methods
- Multi-week programs with periodization support (linear, undulating, block)
- Social features infrastructure (user relationships, sharing permissions)
- Analytics models (volume tracking, strength progression)

🚧 **Deferred (Infrastructure Ready, UI/Integration Pending):**
- **LLM Integration**: Endpoints and data structures ready for AI-powered workout generation
- **Calendar UI**: Database supports workout scheduling; calendar interface to be built
- **Social UI**: Backend supports following, sharing, and permissions; frontend to be implemented
- **Advanced Analytics Dashboard**: Data models ready; visualization dashboards to be built

### Key Features

- 🏋️ **Workout Creation**: Build custom workouts by stitching together exercises and sets with full control over order and structure
- 💪 **Exercise Library**: Access a comprehensive exercise database powered by the Wger API, with automatic synchronization of exercises and muscle groups
- 🔄 **Wger Integration**: Sync exercises from Wger API with support for both full sync (truncate and reload) and partial sync (change data capture)
- 📊 **Detailed Set Tracking**: Log sets with weight (percentage of 1RM or static values), units (lbs/kg), rest time, RIR (Reps in Reserve), and custom notes
- 🎯 **Muscle Group Mapping**: Exercises include primary and secondary muscle groups for better workout planning and analysis
- 👥 **Multi-User Support**: Secure authentication with JWT tokens, allowing multiple users to track their individual workouts
- 📥 **Import/Export**: Import exercises from CSV files or export your exercise library for backup and sharing
- 🔐 **Admin Dashboard**: Full-featured admin interface for managing exercises, muscle groups, and syncing with Wger API

### How It Works

1. **Exercise Database**: The application uses the Wger API to populate a comprehensive exercise library. Administrators can sync exercises from Wger, which automatically creates muscle groups and maps exercises to their primary and secondary muscle targets.

2. **Workout Creation**: Users create workouts by:
   - Selecting exercises from the library
   - Adding exercise instances to their workout in a specific order
   - Adding multiple sets to each exercise instance with detailed tracking data

3. **Set Tracking**: Each set can include:
   - Weight (static value or percentage of 1RM)
   - Unit of measurement (lbs or kg)
   - Rest time between sets
   - RIR (Reps in Reserve) for intensity tracking
   - Custom notes for each set

### Data Model

- **Workouts**: User workouts with date and time
- **Exercises**: Exercise library with name, primary muscle group, and secondary muscle groups (synced from Wger API)
- **Exercise Instances**: Exercises within a workout (with ordering to maintain workout structure)
- **Sets**: Individual sets with weight, unit, rest time, RIR, and notes
- **Muscle Groups**: Categorization system for exercises (automatically created from Wger API)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (optional, for caching and rate limiting)
- Docker and Docker Compose (recommended)

### Installation

1. **Clone the repository**

```sh
git clone <your-repo-url>
cd lift-tracker
```

2. **Set up environment variables**

Create a `.env` file in the `src` directory:

```sh
cd src
touch .env
```

Add the following configuration:

```env
# App Settings
APP_NAME="Lift Tracker"
APP_DESCRIPTION="Workout tracking API"
APP_VERSION="0.1.0"
CONTACT_NAME="Your Name"
CONTACT_EMAIL="your.email@example.com"

# Database
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="your_password"
POSTGRES_SERVER="localhost"  # Use "db" if using docker compose
POSTGRES_PORT=5432
POSTGRES_DB="lift_tracker"

# Security
SECRET_KEY="your-secret-key-here"  # Generate with: openssl rand -hex 32
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin User
ADMIN_NAME="Admin"
ADMIN_EMAIL="admin@example.com"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="your_secure_password"

# Redis (optional)
REDIS_CACHE_HOST="localhost"  # Use "redis" if using docker compose
REDIS_CACHE_PORT=6379

# Environment
ENVIRONMENT="local"  # Options: local, staging, production
```

3. **Run with Docker Compose (Recommended)**

```sh
docker compose up
```

This will start:
- PostgreSQL database
- Redis (if configured)
- FastAPI application
- Worker (for background tasks)

4. **Or run from scratch**

Install dependencies:

```sh
uv sync
```

Start PostgreSQL and Redis (if using Docker):

```sh
docker run -d -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=your_password -e POSTGRES_USER=postgres postgres
docker run -d --name redis -p 6379:6379 redis:alpine
```

Run database migrations:

```sh
cd src
uv run alembic revision --autogenerate -m "Initial migration"
uv run alembic upgrade head
```

Create the first superuser:

```sh
uv run python -m src.scripts.create_first_superuser
```

Start the application:

```sh
uv run uvicorn src.app.main:app --reload
```

5. **Access the API**

- API Documentation: `http://localhost:8000/docs`
- API Base URL: `http://localhost:8000/api/v1`

---

## 📚 API Endpoints

### Authentication

- `POST /api/v1/login` - User login
- `POST /api/v1/logout` - User logout
- `POST /api/v1/user` - Create new user

### Muscle Groups

- `GET /api/v1/muscle-groups` - List all muscle groups
- `GET /api/v1/muscle-group/{id}` - Get muscle group by ID
- `POST /api/v1/muscle-group` - Create muscle group
- `PATCH /api/v1/muscle-group/{id}` - Update muscle group
- `DELETE /api/v1/muscle-group/{id}` - Delete muscle group

### Exercises

- `GET /api/v1/exercises` - List all exercises
- `GET /api/v1/exercise/{id}` - Get exercise by ID
- `POST /api/v1/exercise` - Create exercise
- `PATCH /api/v1/exercise/{id}` - Update exercise
- `DELETE /api/v1/exercise/{id}` - Delete exercise
- `POST /api/v1/exercises/sync-wger` - Sync exercises from Wger API (supports `full_sync` query parameter)
- `GET /api/v1/exercises/export` - Export all exercises as CSV
- `POST /api/v1/exercises/import` - Import exercises from CSV file with change data capture

### Workout Sessions (New System - Recommended)

- `POST /api/v1/workout-session` - Create a new workout session
- `GET /api/v1/workout-sessions` - List all workout sessions for current user (paginated)
- `GET /api/v1/workout-session/{session_id}` - Get a specific workout session with all entries and sets
- `PATCH /api/v1/workout-session/{session_id}` - Update a workout session
- `DELETE /api/v1/workout-session/{session_id}` - Delete a workout session (cascades to entries and sets)
- `POST /api/v1/workout-session/{session_id}/exercise-entry` - Add an exercise entry to a workout session
- `GET /api/v1/workout-session/{session_id}/exercise-entries` - Get all exercise entries for a workout session (paginated)
- `POST /api/v1/exercise-entry/{entry_id}/set` - Add a set to an exercise entry
- `GET /api/v1/exercise-entry/{entry_id}/sets` - Get all sets for an exercise entry (paginated)

### Workouts (Legacy System)

- `GET /api/v1/workouts` - List user's workouts
- `GET /api/v1/workout/{id}` - Get workout by ID
- `POST /api/v1/workout` - Create workout
- `PATCH /api/v1/workout/{id}` - Update workout
- `DELETE /api/v1/workout/{id}` - Delete workout

### Exercise Instances (Legacy System)

- `POST /api/v1/workout/{workout_id}/exercise-instance` - Add exercise to workout
- `DELETE /api/v1/workout/{workout_id}/exercise-instance/{id}` - Remove exercise from workout

### Sets (Legacy System)

- `POST /api/v1/exercise-instance/{id}/set` - Add set to exercise instance
- `PATCH /api/v1/set/{id}` - Update set
- `DELETE /api/v1/set/{id}` - Delete set

### Equipment

- `GET /api/v1/equipment` - List all equipment (paginated, filters by enabled status)
- `GET /api/v1/equipment/{equipment_id}` - Get a specific equipment item
- `POST /api/v1/equipment` - Create equipment (admin only)
- `PATCH /api/v1/equipment/{equipment_id}` - Update equipment (admin only)
- `DELETE /api/v1/equipment/{equipment_id}` - Delete equipment (admin only)
- `GET /api/v1/equipment/export` - Export all equipment as CSV
- `POST /api/v1/equipment/import` - Import equipment from CSV file with change data capture
- `POST /api/v1/equipment/sync-wger` - Sync equipment from Wger API (supports `full_sync` query parameter)

### Workout Templates

- `POST /api/v1/workout-template` - Create a new workout template
- `GET /api/v1/workout-templates` - Get workout templates (user's own and public ones, paginated)
- `GET /api/v1/workout-template/{template_id}` - Get a specific workout template
- `PATCH /api/v1/workout-template/{template_id}` - Update a workout template
- `DELETE /api/v1/workout-template/{template_id}` - Delete a workout template

### Programs

- `POST /api/v1/program` - Create a new training program
- `GET /api/v1/programs` - Get training programs (paginated)
- `GET /api/v1/program/{program_id}` - Get a specific program
- `PATCH /api/v1/program/{program_id}` - Update a program
- `DELETE /api/v1/program/{program_id}` - Delete a program

### 1RM Tracking

- `POST /api/v1/one-rm` - Create or update a 1RM record
- `GET /api/v1/one-rm` - Get 1RM records (paginated)
- `GET /api/v1/one-rm/{one_rm_id}` - Get a specific 1RM record
- `PATCH /api/v1/one-rm/{one_rm_id}` - Update a 1RM record
- `DELETE /api/v1/one-rm/{one_rm_id}` - Delete a 1RM record

### Analytics

- `GET /api/v1/analytics/volume` - Get volume analytics
- `GET /api/v1/analytics/strength-progression` - Get strength progression analytics

---

## 🧪 Testing

The project includes comprehensive test coverage (>95%) using pytest.

### Run Tests

```sh
# Run all tests
uv run pytest

# Run import tests first (catches syntax/import errors before running full suite)
uv run pytest tests/test_model_imports.py tests/test_api_imports.py -v

# Run with coverage report
uv run pytest --cov=src/app --cov-report=html

# Run specific test file
uv run pytest tests/test_workout_sessions.py

# Run tests with verbose output
uv run pytest -v

# Run tests and stop on first failure
uv run pytest -x
```

### Test Structure

**Critical Import Tests (run these first):**
- `tests/test_model_imports.py` - Tests all models and schemas can be imported (catches dataclass field ordering errors)
- `tests/test_api_imports.py` - Tests all API routers can be imported (catches syntax errors)

**Unit Tests:**
- `tests/test_workout_sessions.py` - Workout session API endpoint tests
- `tests/test_scheduled_workouts.py` - Scheduled workout API endpoint tests
- `tests/test_muscle_groups.py` - Muscle group endpoint tests
- `tests/test_exercises.py` - Exercise endpoint tests
- `tests/test_workouts.py` - Workout endpoint tests
- `tests/test_user.py` - User authentication tests

### Pre-commit Testing

Before committing, always run:
```sh
# 1. Test imports (catches syntax and import errors)
uv run pytest tests/test_model_imports.py tests/test_api_imports.py -v

# 2. Run all tests
uv run pytest
```

See `TESTING.md` for more detailed testing information.

---

## 🗄️ Database Migrations

To create new migrations after model changes:

```sh
cd src
uv run alembic revision --autogenerate -m "Description of changes"
uv run alembic upgrade head
```

See `MIGRATION_INSTRUCTIONS.md` for detailed migration steps.

---

## 🏗️ Project Structure

```
lift-tracker/
├── src/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   │   ├── workouts.py
│   │   │   ├── exercises.py
│   │   │   ├── muscle_groups.py
│   │   │   └── users.py
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── workout.py
│   │   │   ├── exercise.py
│   │   │   ├── exercise_instance.py
│   │   │   ├── set.py
│   │   │   └── muscle_group.py
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── crud/             # CRUD operations
│   │   └── core/             # Core utilities
│   ├── migrations/           # Alembic migrations
│   └── scripts/              # Utility scripts
├── tests/                     # Test files
└── docker-compose.yml         # Docker configuration
```

---

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

- **Database**: PostgreSQL connection settings
- **Security**: JWT secret key and token expiration
- **Redis**: Cache and rate limiting configuration
- **Environment**: Set to `production` to hide API docs

### Authentication

The API uses JWT tokens for authentication:

1. Login via `POST /api/v1/login` to get an access token
2. Include token in requests: `Authorization: Bearer <token>`
3. Access tokens expire after 30 minutes (configurable)
4. Refresh tokens are stored as secure HTTP-only cookies

---

## 📝 Usage Examples

### Sync Exercises from Wger API

```bash
# Partial sync (change data capture - only updates new/changed exercises)
curl -X POST "http://localhost:8000/api/v1/exercises/sync-wger?full_sync=false" \
  -H "Authorization: Bearer <your-token>"

# Full sync (truncates all exercises and reloads from Wger)
curl -X POST "http://localhost:8000/api/v1/exercises/sync-wger?full_sync=true" \
  -H "Authorization: Bearer <your-token>"
```

### Create a Workout

```bash
curl -X POST "http://localhost:8000/api/v1/workout" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-15T10:00:00Z"
  }'
```

### Build a Workout: Add Exercises and Sets

```bash
# Step 1: Add an exercise to the workout (creates an exercise instance)
curl -X POST "http://localhost:8000/api/v1/workout/1/exercise-instance" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_id": 1,
    "order": 0
  }'

# Step 2: Add sets to the exercise instance
curl -X POST "http://localhost:8000/api/v1/exercise-instance/1/set" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "weight_value": 135.5,
    "weight_type": "static",
    "unit": "lbs",
    "rest_time_seconds": 90,
    "rir": 2,
    "notes": "Felt strong today"
  }'

# Repeat steps 1-2 to build your complete workout with multiple exercises and sets
```

### Export/Import Exercises

```bash
# Export exercises to CSV
curl -X GET "http://localhost:8000/api/v1/exercises/export" \
  -H "Authorization: Bearer <your-token>" \
  --output exercises.csv

# Import exercises from CSV (with change data capture)
curl -X POST "http://localhost:8000/api/v1/exercises/import" \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@exercises.csv"
```

---