# Lift Tracker Frontend

React + TypeScript frontend for the Lift Tracker application.

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
- **Home Page**: View all workouts or see "No workouts recorded" message
- **Create Workout**: Build workouts by selecting exercises and adding sets with:
  - Weight value and type (static or percentage of 1RM)
  - Unit (lbs or kg)
  - Rest time
  - RIR (Reps in Reserve)
  - Notes

## Project Structure

```
frontend/
├── src/
│   ├── contexts/       # React context for authentication
│   ├── pages/         # Page components (Login, Signup, Home, CreateWorkout)
│   ├── services/      # API service layer
│   ├── App.tsx        # Main app component with routing
│   └── main.tsx       # Entry point
├── package.json
└── vite.config.ts
```

## Environment

Make sure the backend API is running on `http://localhost:8000` or update the proxy configuration in `vite.config.ts`.

