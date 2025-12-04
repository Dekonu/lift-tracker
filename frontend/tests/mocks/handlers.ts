import { http, HttpResponse } from 'msw';

export const handlers = [
  // Workouts
  http.get('/api/v1/workout-sessions', () => {
    return HttpResponse.json({
      data: [
        { id: 1, name: 'Push Day', started_at: '2024-01-01T10:00:00Z' },
      ],
      total_count: 1,
      has_more: false,
      page: 1,
      items_per_page: 20,
    });
  }),

  http.post('/api/v1/workout-sessions', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      { id: 1, ...body, created_at: new Date().toISOString() },
      { status: 201 }
    );
  }),

  // Exercises
  http.get('/api/v1/exercises', () => {
    return HttpResponse.json({
      data: [
        { id: 1, name: 'Bench Press', primary_muscle_group_ids: [1] },
        { id: 2, name: 'Squat', primary_muscle_group_ids: [2] },
      ],
      total_count: 2,
      has_more: false,
    });
  }),

  // Auth
  http.post('/api/v1/auth/login', async ({ request }) => {
    const body = (await request.json()) as { email: string; password: string };
    if (body.email === 'test@example.com' && body.password === 'password') {
      return HttpResponse.json({
        access_token: 'mock-token',
        token_type: 'bearer',
      });
    }
    return HttpResponse.json(
      { detail: 'Invalid credentials' },
      { status: 401 }
    );
  }),
];

