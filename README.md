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
- **User personal info** (gender, weight, height, birthdate, net_weight_goal, strength_goals) via `GET`/`PATCH` `/api/v1/user/me/`
- **Core exercise flag** (`is_core`) on exercises for programs/LLM—exposed in exercise list/detail and updatable via `PATCH /api/v1/exercise/{id}`
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

Base URL: `http://localhost:8000/api/v1`. All paginated list endpoints accept `page` and `items_per_page` unless noted. Authenticated routes require `Authorization: Bearer <access_token>` unless marked public.

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/login` | Login (form: username=email, password). Returns access token; sets refresh token cookie. |
| `POST` | `/refresh` | Refresh access token using refresh token cookie. |
| `POST` | `/logout` | Logout (invalidates tokens, clears refresh cookie). |
| `POST` | `/user` | Create new user (public). |

### Users

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/user/me/` | Current user (includes personal info: gender, weight_lbs, height_ft, height_in, birthdate, net_weight_goal, strength_goals). |
| `PATCH` | `/user/me` | Update current user (name, email, profile_image_url, and optional personal info above). |
| `DELETE` | `/user/me` | Delete current user and invalidate token. |
| `GET` | `/users` | List users (paginated). |
| `GET` | `/user/{user_id}` | Get user by ID. |
| `GET` | `/user/{user_id}/tier` | Get user's tier info. |
| `GET` | `/user/{user_id}/rate_limits` | Get user's rate limits (superuser). |
| `PATCH` | `/user/{user_id}/tier` | Update user's tier (superuser). |
| `DELETE` | `/db_user/{user_id}` | Hard delete user (superuser). |

### User Profile (goals, experience, training preferences)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/user-profile` | Create current user's profile. |
| `GET` | `/user-profile/me` | Get current user's profile. |
| `PATCH` | `/user-profile/me` | Update current user's profile. |

### Muscle Groups

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/muscle-groups` | List muscle groups (paginated). |
| `GET` | `/muscle-group/{muscle_group_id}` | Get muscle group by ID. |
| `POST` | `/muscle-group` | Create muscle group. |
| `PATCH` | `/muscle-group/{muscle_group_id}` | Update muscle group. |
| `DELETE` | `/muscle-group/{muscle_group_id}` | Delete muscle group. |

### Exercises

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/exercises` | List exercises (paginated; optional `equipment_ids` comma-separated filter). Returns `is_core` for each exercise. Non-admins see only enabled exercises. |
| `GET` | `/exercise/{exercise_id}` | Get exercise by ID (includes `is_core`). |
| `POST` | `/exercise` | Create exercise (includes optional `is_core`). |
| `PATCH` | `/exercise/{exercise_id}` | Update exercise (including `is_core`). |
| `DELETE` | `/exercise/{exercise_id}` | Delete exercise. |
| `POST` | `/exercises/sync-wger` | Sync from Wger API (query: `full_sync` true/false). |
| `GET` | `/exercises/export` | Export exercises as CSV. |
| `POST` | `/exercises/import` | Import exercises from CSV (change data capture). |

### Exercise–Equipment Links

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/exercise/{exercise_id}/equipment/{equipment_id}` | Link equipment to exercise. |
| `DELETE` | `/exercise/{exercise_id}/equipment/{equipment_id}` | Unlink equipment from exercise. |
| `GET` | `/exercise/{exercise_id}/equipment` | List equipment for exercise (paginated). |

### Equipment

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/equipment` | List equipment (paginated; filter by enabled). |
| `GET` | `/equipment/{equipment_id}` | Get equipment by ID. |
| `POST` | `/equipment` | Create equipment (admin). |
| `PATCH` | `/equipment/{equipment_id}` | Update equipment (admin). |
| `DELETE` | `/equipment/{equipment_id}` | Delete equipment (admin). |
| `GET` | `/equipment/export` | Export equipment as CSV. |
| `POST` | `/equipment/import` | Import equipment from CSV. |
| `POST` | `/equipment/sync-wger` | Sync equipment from Wger (`full_sync` query). |

### Workout Sessions (recommended)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/workout-session` | Create workout session. |
| `GET` | `/workout-sessions` | List current user's sessions (paginated). |
| `GET` | `/workout-session/{session_id}` | Get session with entries and sets. |
| `PATCH` | `/workout-session/{session_id}` | Update session. |
| `DELETE` | `/workout-session/{session_id}` | Delete session (cascades). |
| `POST` | `/workout-session/{session_id}/exercise-entry` | Add exercise entry to session. |
| `GET` | `/workout-session/{session_id}/exercise-entries` | List exercise entries (paginated). |
| `POST` | `/exercise-entry/{entry_id}/set` | Add set to entry. |
| `GET` | `/exercise-entry/{entry_id}/sets` | List sets for entry (paginated). |

### Set Entries (workout-session sets)

| Method | Path | Description |
|--------|------|-------------|
| `PATCH` | `/set-entry/{set_id}` | Update a set (weight, reps, RIR, etc.). |

### Workout Templates

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/workout-template` | Create template. |
| `GET` | `/workout-templates` | List templates (own + public, paginated). |
| `GET` | `/workout-template/{template_id}` | Get template. |
| `PATCH` | `/workout-template/{template_id}` | Update template. |
| `DELETE` | `/workout-template/{template_id}` | Delete template. |
| `POST` | `/workout-template/{template_id}/apply` | Apply template (e.g. create session from template). |

### Scheduled Workouts

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/scheduled-workout` | Create scheduled workout. |
| `GET` | `/scheduled-workouts` | List scheduled workouts (paginated). |
| `GET` | `/scheduled-workout/{scheduled_id}` | Get scheduled workout. |
| `PATCH` | `/scheduled-workout/{scheduled_id}` | Update scheduled workout. |
| `DELETE` | `/scheduled-workout/{scheduled_id}` | Delete scheduled workout. |
| `POST` | `/program/{program_id}/schedule` | Schedule a program (bulk create scheduled workouts). |

### Programs

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/program` | Create program. |
| `GET` | `/programs` | List programs (paginated). |
| `GET` | `/program/{program_id}` | Get program. |
| `PATCH` | `/program/{program_id}` | Update program. |
| `DELETE` | `/program/{program_id}` | Delete program. |
| `GET` | `/program/{program_id}/weeks` | List program weeks (paginated). |
| `POST` | `/program/{program_id}/week` | Add week to program. |
| `PATCH` | `/program/{program_id}/week/{week_id}` | Update program week. |
| `GET` | `/program/{program_id}/days` | List program day assignments (paginated). |
| `POST` | `/program/{program_id}/day` | Add day assignment (template + day label). |
| `PATCH` | `/program/{program_id}/day/{assignment_id}` | Update day assignment. |
| `DELETE` | `/program/{program_id}/day/{assignment_id}` | Delete day assignment. |

### Workouts (legacy)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/workout` | Create workout. |
| `GET` | `/workouts` | List user's workouts (paginated). |
| `GET` | `/workout/{workout_id}` | Get workout. |
| `PATCH` | `/workout/{workout_id}` | Update workout. |
| `DELETE` | `/workout/{workout_id}` | Delete workout. |
| `POST` | `/workout/{workout_id}/exercise-instance` | Add exercise instance. |
| `DELETE` | `/workout/{workout_id}/exercise-instance/{exercise_instance_id}` | Remove exercise instance. |
| `POST` | `/exercise-instance/{exercise_instance_id}/set` | Add set to instance. |
| `PATCH` | `/set/{set_id}` | Update set. |
| `DELETE` | `/set/{set_id}` | Delete set. |

### 1RM

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/one-rm` | Create or update 1RM record. |
| `GET` | `/one-rm` | List 1RM records (paginated). |
| `GET` | `/one-rm/{one_rm_id}` | Get 1RM record. |
| `PATCH` | `/one-rm/{one_rm_id}` | Update 1RM record. |
| `DELETE` | `/one-rm/{one_rm_id}` | Delete 1RM record. |

### Analytics

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/analytics/volume` | Get volume analytics (paginated). |
| `POST` | `/analytics/volume/calculate` | Trigger volume calculation. |
| `GET` | `/analytics/strength-progression` | Get strength progression (paginated). |
| `POST` | `/analytics/strength-progression/calculate` | Trigger strength progression calculation. |

### Dashboard

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dashboard/stats` | Dashboard stats for current user. |

### Posts (social)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/{username}/post` | Create post. |
| `GET` | `/{username}/posts` | List user's posts (paginated). |
| `GET` | `/{username}/post/{id}` | Get post. |
| `PATCH` | `/{username}/post/{id}` | Update post. |
| `DELETE` | `/{username}/post/{id}` | Delete post. |
| `DELETE` | `/{username}/db_post/{id}` | Hard delete post (superuser). |

### Tiers & Rate Limits (admin)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/tier` | Create tier (superuser). |
| `GET` | `/tiers` | List tiers (paginated). |
| `GET` | `/tier/{name}` | Get tier by name. |
| `PATCH` | `/tier/{name}` | Update tier (superuser). |
| `DELETE` | `/tier/{name}` | Delete tier (superuser). |
| `POST` | `/tier/{tier_name}/rate_limit` | Create rate limit for tier (superuser). |
| `GET` | `/tier/{tier_name}/rate_limits` | List rate limits for tier (paginated). |
| `GET` | `/tier/{tier_name}/rate_limit/{id}` | Get rate limit. |
| `PATCH` | `/tier/{tier_name}/rate_limit/{id}` | Update rate limit (superuser). |
| `DELETE` | `/tier/{tier_name}/rate_limit/{id}` | Delete rate limit (superuser). |

### Background Tasks

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/tasks/task` | Enqueue background task (body: `message`). |
| `GET` | `/tasks/task/{task_id}` | Get task status/result. |

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