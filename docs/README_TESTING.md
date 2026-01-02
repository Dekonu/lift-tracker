# Testing Setup for GitHub Actions

## Overview

The project now includes comprehensive testing for both backend and frontend, with GitHub Actions workflows configured to run all tests automatically.

## Workflow Structure

### Main Tests Workflow (`.github/workflows/tests.yml`)

This workflow runs all tests in parallel:

1. **Backend Tests** - Runs Python/pytest tests
2. **Frontend Tests** - Runs Vitest unit and integration tests
3. **Frontend E2E Tests** - Runs Playwright end-to-end tests (requires backend server)

### Frontend-Only Tests Workflow (`.github/workflows/frontend-tests.yml`)

This workflow runs only when frontend files change, for faster feedback on frontend-only PRs.

## Running Tests Locally

### Backend Tests

```bash
# Run all backend tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/app --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests only
npm run test:integration

# Run E2E tests (requires backend running)
npm run test:e2e

# Run with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

## Test Structure

### Backend Tests
- Location: `tests/`
- Framework: pytest
- Coverage target: 95%

### Frontend Tests
- **Unit Tests**: `frontend/tests/unit/`
- **Integration Tests**: `frontend/tests/integration/`
- **E2E Tests**: `frontend/tests/e2e/`
- Framework: Vitest (unit/integration), Playwright (E2E)

## CI/CD Integration

All tests run automatically on:
- Push to any branch
- Pull requests

Test results and coverage reports are uploaded as artifacts in GitHub Actions.

## Troubleshooting

### Frontend tests fail in CI

1. Ensure `package-lock.json` is committed
2. Check that all test dependencies are in `devDependencies`
3. Verify `vitest.config.ts` paths match your project structure

### E2E tests fail

1. Ensure backend server starts successfully
2. Check that Playwright browsers are installed: `npx playwright install`
3. Verify backend is accessible at `http://localhost:8000`

### Coverage not generating

1. Ensure `@vitest/coverage-v8` is installed
2. Check `vitest.config.ts` coverage configuration
3. Verify test files are in the correct directories

