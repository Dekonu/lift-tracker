# Testing Guide

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_workout_sessions.py
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Tests and Stop on First Failure
```bash
pytest -x
```

### Run Tests Matching a Pattern
```bash
pytest -k "test_create"
```

## Test Structure

### Import Tests (Critical)
These tests ensure the application can start without errors:
- `tests/test_model_imports.py` - Tests all models and schemas can be imported
- `tests/test_api_imports.py` - Tests all API routers can be imported

**Run these first to catch import errors:**
```bash
pytest tests/test_model_imports.py tests/test_api_imports.py -v
```

### Unit Tests
- `tests/test_workout_sessions.py` - Workout session API endpoints
- `tests/test_scheduled_workouts.py` - Scheduled workout API endpoints

## Pre-commit Testing

Before committing, always run:
```bash
# 1. Test imports (catches syntax and import errors)
pytest tests/test_model_imports.py tests/test_api_imports.py -v

# 2. Run all tests
pytest

# 3. Check linting (if configured)
# flake8 src/
# black --check src/
```

## Common Issues

### Field Ordering Errors
If you see `TypeError: non-default argument follows default argument`:
- Check SQLAlchemy models - non-default fields must come before default fields
- Check function signatures - parameters with defaults must come after those without

### Forward Reference Errors
If you see `TypeError: unsupported operand type(s) for |: 'str' and 'NoneType'`:
- Ensure forward references use `Annotated` with `Field(default=None)`
- Call `model_rebuild()` after all schemas are defined
- Use `TYPE_CHECKING` for forward references

## Continuous Integration

Add to your CI/CD pipeline:
```yaml
- name: Run Import Tests
  run: pytest tests/test_model_imports.py tests/test_api_imports.py -v

- name: Run All Tests
  run: pytest --cov=src --cov-report=xml
```

