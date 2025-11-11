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
</p>

---

## 📖 About

**Lift Tracker** is a multi-user workout tracking application that allows users to log and manage their training sessions. The API provides comprehensive tracking of workouts, exercises, sets, and muscle groups with support for various weight measurement systems.

### Key Features

- 🏋️ **Workout Management**: Create and track workouts with date/time
- 💪 **Exercise Library**: Manage exercises with primary and secondary muscle groups
- 📊 **Set Tracking**: Log sets with weight (percentage of 1RM or static), units (lbs/kg), rest time, RIR (Reps in Reserve), and notes
- 👥 **Multi-User Support**: Secure authentication with JWT tokens
- 🔐 **User Authentication**: JWT-based authentication with refresh tokens
- 📈 **Comprehensive Data**: Track all aspects of your training sessions

### Data Model

- **Workouts**: User workouts with date and time
- **Exercises**: Exercise library with name, primary muscle group, and secondary muscle groups
- **Exercise Instances**: Exercises within a workout (with ordering)
- **Sets**: Individual sets with weight, unit, rest time, RIR, and notes
- **Muscle Groups**: Categorization system for exercises

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

### Workouts

- `GET /api/v1/workouts` - List user's workouts
- `GET /api/v1/workout/{id}` - Get workout by ID
- `POST /api/v1/workout` - Create workout
- `PATCH /api/v1/workout/{id}` - Update workout
- `DELETE /api/v1/workout/{id}` - Delete workout

### Exercise Instances

- `POST /api/v1/workout/{workout_id}/exercise-instance` - Add exercise to workout
- `DELETE /api/v1/workout/{workout_id}/exercise-instance/{id}` - Remove exercise from workout

### Sets

- `POST /api/v1/exercise-instance/{id}/set` - Add set to exercise instance
- `PATCH /api/v1/set/{id}` - Update set
- `DELETE /api/v1/set/{id}` - Delete set

---

## 🧪 Testing

The project includes comprehensive test coverage (>95%) using pytest.

### Run Tests

```sh
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src/app --cov-report=html

# Run specific test file
uv run pytest tests/test_workouts.py
```

### Test Structure

- `tests/test_muscle_groups.py` - Muscle group endpoint tests
- `tests/test_exercises.py` - Exercise endpoint tests
- `tests/test_workouts.py` - Workout endpoint tests
- `tests/test_user.py` - User authentication tests

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

### Create a Workout

```bash
curl -X POST "http://localhost:8000/api/v1/workout" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-15T10:00:00Z"
  }'
```

### Add an Exercise to a Workout

```bash
curl -X POST "http://localhost:8000/api/v1/workout/1/exercise-instance" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_id": 1,
    "order": 0
  }'
```

### Add a Set

```bash
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
```

---

## 🚀 Production Deployment

For production deployment:

1. Set `ENVIRONMENT=production` in `.env`
2. Use Gunicorn with Uvicorn workers
3. Configure NGINX as reverse proxy
4. Set up proper database backups
5. Use secure Redis configuration

See the original boilerplate documentation for detailed production setup instructions.

---

## 📄 License

MIT License - see `LICENSE.md` for details

---

## 🤝 Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for guidelines.

---

## 📞 Support

For issues and questions, please open an issue on GitHub.
