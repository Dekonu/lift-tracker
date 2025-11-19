import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface ExerciseInstance {
  id: number
  exercise_id: number
  order: number
  sets: Set[]
}

interface Set {
  id: number
  weight_value: number
  weight_type: string
  unit: string
  rest_time_seconds?: number
  rir?: number
  notes?: string
}

interface Workout {
  id: number
  date: string
  exercise_instances?: ExerciseInstance[]
}

export default function Home() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [workouts, setWorkouts] = useState<Workout[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchWorkouts()
  }, [])

  const fetchWorkouts = async () => {
    try {
      const response = await api.get('/v1/workouts?page=1&items_per_page=20')
      setWorkouts(response.data.data || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch workouts')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
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

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <div className="loading">Loading workouts...</div>
        </div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : workouts.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 40px' }}>
          <h2 style={{ marginBottom: '20px' }}>No workouts recorded</h2>
          <p style={{ marginBottom: '30px' }}>
            Start tracking your workouts by creating your first one!
          </p>
          <button 
            className="btn btn-primary" 
            onClick={() => navigate('/workout/create')}
            style={{ fontSize: '18px', padding: '14px 32px' }}
          >
            Create Workout
          </button>
        </div>
      ) : (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
            <h2>Your Workouts</h2>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/workout/create')}
            >
              Create Workout
            </button>
          </div>
          {workouts.map((workout) => (
            <div key={workout.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3>{formatDate(workout.date)}</h3>
              </div>
              {workout.exercise_instances && workout.exercise_instances.length > 0 ? (
                <div>
                  <p style={{ marginBottom: '16px', fontWeight: '600', fontSize: '16px' }}>
                    {workout.exercise_instances.length} exercise{workout.exercise_instances.length !== 1 ? 's' : ''}
                  </p>
                  {workout.exercise_instances.map((instance) => (
                    <div 
                      key={instance.id} 
                      style={{ 
                        marginBottom: '12px', 
                        padding: '16px', 
                        background: 'linear-gradient(135deg, rgba(230, 213, 247, 0.15) 0%, rgba(168, 230, 207, 0.15) 100%)',
                        borderRadius: '12px',
                        border: '1px solid rgba(230, 213, 247, 0.3)',
                        transition: 'all 0.3s ease',
                        color: '#1A1A1A'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateX(4px)'
                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(230, 213, 247, 0.2)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateX(0)'
                        e.currentTarget.style.boxShadow = 'none'
                      }}
                    >
                      <p style={{ fontWeight: '600', marginBottom: '4px' }}>Exercise #{instance.order}</p>
                      {instance.sets && instance.sets.length > 0 && (
                        <p style={{ fontSize: '14px', marginTop: '4px' }}>
                          {instance.sets.length} set{instance.sets.length !== 1 ? 's' : ''}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p>No exercises in this workout</p>
              )}
            </div>
          ))}
        </>
      )}
    </div>
  )
}

