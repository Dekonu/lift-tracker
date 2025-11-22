import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface ExerciseEntry {
  id: number
  exercise_id: number
  order: number
  sets: SetEntry[]
}

interface SetEntry {
  id: number
  set_number: number
  weight_kg?: number
  reps?: number
  rir?: number
  rpe?: number
  percentage_of_1rm?: number
  rest_seconds?: number
  tempo?: string
  notes?: string
  is_warmup: boolean
}

interface WorkoutSession {
  id: number
  name?: string
  started_at: string
  exercise_entries?: ExerciseEntry[]
}

export default function Home() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [workouts, setWorkouts] = useState<WorkoutSession[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)
  const [selectedWorkout, setSelectedWorkout] = useState<WorkoutSession | null>(null)

  useEffect(() => {
    fetchWorkouts(true)
  }, [])

  // Handle date selection from URL query parameter (e.g., after creating workout)
  useEffect(() => {
    const dateParam = searchParams.get('date')
    if (dateParam) {
      const date = new Date(dateParam)
      if (!isNaN(date.getTime())) {
        setCurrentMonth(date)
        setSelectedDate(date)
        // Find workout for this date
        const workoutsForDate = workouts.filter(workout => {
          const workoutDate = new Date(workout.started_at).toISOString().split('T')[0]
          return workoutDate === dateParam
        })
        if (workoutsForDate.length > 0) {
          setSelectedWorkout(workoutsForDate[0])
        }
        // Clear the query parameter
        navigate('/home', { replace: true })
      }
    }
  }, [searchParams, workouts, navigate])

  const fetchWorkouts = async (showLoading = false) => {
    try {
      if (showLoading) {
        setLoading(true)
      }
      // Fetch a large number of workouts to populate the calendar
      const response = await api.get('/v1/workout-sessions?page=1&items_per_page=1000')
      const workoutsData = response.data.data || []
      setWorkouts(workoutsData)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch workouts')
    } finally {
      if (showLoading) {
        setLoading(false)
      }
    }
  }

  const getWorkoutsForDate = (date: Date): WorkoutSession[] => {
    const dateStr = date.toISOString().split('T')[0]
    return workouts.filter(workout => {
      const workoutDate = new Date(workout.started_at).toISOString().split('T')[0]
      return workoutDate === dateStr
    })
  }

  const getDaysInMonth = (date: Date): Date[] => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDayOfWeek = firstDay.getDay()

    const days: Date[] = []
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(new Date(year, month, -i))
    }
    
    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day))
    }
    
    return days
  }

  const handleDateClick = (date: Date) => {
    const workoutsForDate = getWorkoutsForDate(date)
    if (workoutsForDate.length > 0) {
      setSelectedDate(date)
      setSelectedWorkout(workoutsForDate[0]) // For now, show first workout if multiple
    } else {
      setSelectedDate(date)
      setSelectedWorkout(null)
    }
  }

  const handleDeleteWorkout = async (workoutId: number) => {
    if (!window.confirm('Are you sure you want to delete this workout? This action cannot be undone.')) {
      return
    }
    
    try {
      await api.delete(`/v1/workout-session/${workoutId}`)
      // Remove from local state immediately for instant UI update
      setWorkouts(prevWorkouts => prevWorkouts.filter(w => w.id !== workoutId))
      // Also refresh from server to ensure consistency
      await fetchWorkouts()
      setSelectedDate(null)
      setSelectedWorkout(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete workout')
      // Refresh workouts on error to ensure state is correct
      await fetchWorkouts()
    }
  }

  const handleEditWorkout = (workout: WorkoutSession) => {
    // Navigate to edit workout page (we'll create this or use the create page with edit mode)
    navigate(`/workout/edit/${workout.id}`)
  }

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentMonth)
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1)
    } else {
      newDate.setMonth(newDate.getMonth() + 1)
    }
    setCurrentMonth(newDate)
    setSelectedDate(null)
    setSelectedWorkout(null)
  }

  const goToToday = () => {
    const today = new Date()
    setCurrentMonth(today)
    setSelectedDate(null)
    setSelectedWorkout(null)
  }

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric'
    })
  }

  const formatTime = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
    'July', 'August', 'September', 'October', 'November', 'December']
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  const days = getDaysInMonth(currentMonth)
  const today = new Date()
  const isToday = (date: Date) => {
    return date.toDateString() === today.toDateString()
  }

  if (loading) {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <div className="loading">Loading workouts...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', flexWrap: 'wrap', gap: '16px' }}>
        <h1>Welcome, {user?.name}!</h1>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {user?.is_superuser && (
            <button 
              className="btn btn-secondary" 
              onClick={() => navigate('/admin')}
            >
              Admin Dashboard
            </button>
          )}
          <button className="btn btn-secondary" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      {error && <div className="error" style={{ marginBottom: '20px' }}>{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: selectedDate ? '1fr 400px' : '1fr', gap: '24px' }}>
        {/* Calendar View */}
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <button
                className="btn btn-secondary"
                onClick={() => navigateMonth('prev')}
                style={{ padding: '8px 16px', fontSize: '14px' }}
              >
                ← Previous
              </button>
              <h2 style={{ margin: 0, minWidth: '200px', textAlign: 'center' }}>
                {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
              </h2>
              <button
                className="btn btn-secondary"
                onClick={() => navigateMonth('next')}
                style={{ padding: '8px 16px', fontSize: '14px' }}
              >
                Next →
              </button>
            </div>
            <button
              className="btn btn-secondary"
              onClick={goToToday}
              style={{ padding: '8px 16px', fontSize: '14px' }}
            >
              Today
            </button>
          </div>

          {/* Calendar Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '8px' }}>
            {/* Day Headers */}
            {dayNames.map(day => (
              <div
                key={day}
                style={{
                  textAlign: 'center',
                  fontWeight: '600',
                  padding: '8px',
                  color: '#666',
                  fontSize: '14px'
                }}
              >
                {day}
              </div>
            ))}

            {/* Calendar Days */}
            {days.map((date, index) => {
              const workoutsForDate = getWorkoutsForDate(date)
              const hasWorkout = workoutsForDate.length > 0
              const isCurrentMonth = date.getMonth() === currentMonth.getMonth()
              const isSelected = selectedDate && date.toDateString() === selectedDate.toDateString()

              return (
                <div
                  key={index}
                  onClick={() => handleDateClick(date)}
                  style={{
                    aspectRatio: '1',
                    padding: '8px',
                    border: isSelected 
                      ? '2px solid #6366f1' 
                      : isToday(date) 
                        ? '2px solid #10b981' 
                        : '1px solid rgba(0, 0, 0, 0.1)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    backgroundColor: isSelected
                      ? 'rgba(99, 102, 241, 0.1)'
                      : isToday(date)
                        ? 'rgba(16, 185, 129, 0.1)'
                        : hasWorkout
                          ? 'rgba(230, 213, 247, 0.15)'
                          : 'transparent',
                    opacity: isCurrentMonth ? 1 : 0.4,
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative'
                  }}
                  onMouseEnter={(e) => {
                    if (isCurrentMonth) {
                      e.currentTarget.style.backgroundColor = hasWorkout
                        ? 'rgba(230, 213, 247, 0.25)'
                        : 'rgba(0, 0, 0, 0.05)'
                      e.currentTarget.style.transform = 'scale(1.05)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (isCurrentMonth) {
                      e.currentTarget.style.backgroundColor = isSelected
                        ? 'rgba(99, 102, 241, 0.1)'
                        : isToday(date)
                          ? 'rgba(16, 185, 129, 0.1)'
                          : hasWorkout
                            ? 'rgba(230, 213, 247, 0.15)'
                            : 'transparent'
                      e.currentTarget.style.transform = 'scale(1)'
                    }
                  }}
                >
                  <span style={{ 
                    fontSize: '14px', 
                    fontWeight: isToday(date) ? '700' : '500',
                    color: isCurrentMonth ? '#1A1A1A' : '#999'
                  }}>
                    {date.getDate()}
                  </span>
                  {hasWorkout && (
                    <div style={{
                      position: 'absolute',
                      bottom: '4px',
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: '#6366f1'
                    }} />
                  )}
                </div>
              )
            })}
          </div>

          {/* Legend */}
          <div style={{ 
            display: 'flex', 
            gap: '16px', 
            marginTop: '20px', 
            paddingTop: '20px', 
            borderTop: '1px solid rgba(0, 0, 0, 0.1)',
            flexWrap: 'wrap',
            justifyContent: 'center'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '16px', height: '16px', border: '2px solid #10b981', borderRadius: '4px' }} />
              <span style={{ fontSize: '12px', color: '#666' }}>Today</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '16px', height: '16px', backgroundColor: 'rgba(230, 213, 247, 0.15)', borderRadius: '4px' }} />
              <span style={{ fontSize: '12px', color: '#666' }}>Has Workout</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '16px', height: '16px', border: '2px solid #6366f1', borderRadius: '4px' }} />
              <span style={{ fontSize: '12px', color: '#666' }}>Selected</span>
            </div>
          </div>
        </div>

        {/* Workout Details Sidebar */}
        {selectedDate && (
          <div className="card" style={{ padding: '24px', maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0 }}>{formatDate(selectedDate)}</h3>
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setSelectedDate(null)
                  setSelectedWorkout(null)
                }}
                style={{ padding: '4px 12px', fontSize: '12px' }}
              >
                ×
              </button>
            </div>

            {selectedWorkout ? (
              <div>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
                  <button
                    className="btn btn-secondary"
                    onClick={() => handleEditWorkout(selectedWorkout)}
                    style={{ flex: 1, fontSize: '14px', padding: '8px 16px' }}
                  >
                    Edit
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDeleteWorkout(selectedWorkout.id)}
                    style={{ flex: 1, fontSize: '14px', padding: '8px 16px' }}
                  >
                    Delete
                  </button>
                </div>
                
                {selectedWorkout.exercise_entries && selectedWorkout.exercise_entries.length > 0 ? (
                  <div>
                    <p style={{ marginBottom: '16px', fontWeight: '600', fontSize: '16px' }}>
                      {selectedWorkout.exercise_entries.length} exercise{selectedWorkout.exercise_entries.length !== 1 ? 's' : ''}
                    </p>
                    {selectedWorkout.exercise_entries.map((entry) => (
                      <div 
                        key={entry.id} 
                        style={{ 
                          marginBottom: '12px', 
                          padding: '16px', 
                          background: 'linear-gradient(135deg, rgba(230, 213, 247, 0.15) 0%, rgba(168, 230, 207, 0.15) 100%)',
                          borderRadius: '12px',
                          border: '1px solid rgba(230, 213, 247, 0.3)',
                          transition: 'all 0.3s ease',
                          color: '#1A1A1A'
                        }}
                      >
                        <p style={{ fontWeight: '600', marginBottom: '4px' }}>Exercise #{entry.order}</p>
                        {entry.sets && entry.sets.length > 0 && (
                          <p style={{ fontSize: '14px', marginTop: '4px' }}>
                            {entry.sets.length} set{entry.sets.length !== 1 ? 's' : ''}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No exercises in this workout</p>
                )}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                <p style={{ marginBottom: '20px', color: '#666' }}>
                  No workout recorded for this date
                </p>
                <button 
                  className="btn btn-primary" 
                  onClick={() => {
                    // Navigate to create workout with pre-filled date
                    const dateStr = selectedDate.toISOString().split('T')[0]
                    navigate(`/workout/create?date=${dateStr}`)
                  }}
                >
                  Create Workout
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Workout Button */}
      <div style={{ marginTop: '24px', textAlign: 'center' }}>
        <button 
          className="btn btn-primary" 
          onClick={() => navigate('/workout/create')}
          style={{ fontSize: '16px', padding: '12px 24px' }}
        >
          Create New Workout
        </button>
      </div>
    </div>
  )
}
