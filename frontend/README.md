# Lift Tracker Frontend

Next.js 14 + TypeScript frontend for the Lift Tracker application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000` and proxy API requests to `http://localhost:8000`.

## Features

- **Login/Signup**: Email-based authentication (no username required)
- **Dashboard**: View workout statistics and upcoming workouts
- **Calendar**: Schedule and manage workouts
- **Workouts**: Create, edit, and track workout sessions
- **Exercises**: Browse and search exercise library
- **Programs**: Create and manage training programs
- **Analytics**: View workout analytics and progress

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Public routes (login, signup)
│   ├── (dashboard)/       # Protected routes (dashboard, workouts, etc.)
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── providers.tsx      # React Query & Auth providers
├── lib/                    # Shared utilities
│   ├── api/               # API client
│   ├── hooks/             # React Query hooks
│   └── stores/            # Zustand stores
├── tests/                  # Test files
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # E2E tests (Playwright)
├── public/                 # Static assets
├── next.config.js         # Next.js configuration
└── package.json
```

## Environment

Make sure the backend API is running on `http://localhost:8000` or update the proxy configuration in `next.config.js`.

## Testing

```bash
# Run unit tests
npm run test:unit

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e

# Run all tests with coverage
npm run test:coverage
```

