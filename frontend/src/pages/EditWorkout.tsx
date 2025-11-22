import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
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

export default function EditWorkout() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [workout, setWorkout] = useState<WorkoutSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [workoutDate, setWorkoutDate] = useState<Date>(new Date())

  useEffect(() => {
    if (id) {
      fetchWorkout()
    }
  }, [id])

  const fetchWorkout = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/v1/workout-session/${id}`)
      const workoutData = response.data
      setWorkout(workoutData)
      setWorkoutDate(new Date(workoutData.started_at))
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch workout')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    
    setError('')
    setSaving(true)

    try {
      await api.patch(`/v1/workout-session/${id}`, {
        started_at: workoutDate.toISOString()
      })
      navigate('/home')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update workout')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!id) return
    
    if (!window.confirm('Are you sure you want to delete this workout? This action cannot be undone.')) {
      return
    }

    try {
      await api.delete(`/v1/workout-session/${id}`)
      // Navigate to home - the Home component will refresh workouts on mount
      navigate('/home')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete workout')
    }
  }

  if (loading) {
    return <div className="container">Loading...</div>
  }

  if (!workout) {
    return (
      <div className="container">
        <div className="error">Workout not found</div>
        <button className="btn btn-secondary" onClick={() => navigate('/home')}>
          Back to Home
        </button>
      </div>
    )
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Edit Workout</h1>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-danger" onClick={handleDelete}>
            Delete
          </button>
          <button className="btn btn-secondary" onClick={() => navigate('/home')}>
            Cancel
          </button>
        </div>
      </div>

      {error && <div className="error" style={{ marginBottom: '20px' }}>{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group" style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>
            Workout Date & Time
          </label>
          <input
            type="datetime-local"
            value={workoutDate.toISOString().slice(0, 16)}
            onChange={(e) => setWorkoutDate(new Date(e.target.value))}
            required
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid rgba(0, 0, 0, 0.1)',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
          <p style={{ marginTop: '4px', fontSize: '12px', color: '#666' }}>
            Select the date and time when this workout was performed
          </p>
        </div>

        {workout.exercise_entries && workout.exercise_entries.length > 0 && (
          <div className="card" style={{ marginBottom: '24px' }}>
            <h3 style={{ marginBottom: '16px' }}>
              {workout.exercise_entries.length} Exercise{workout.exercise_entries.length !== 1 ? 's' : ''}
            </h3>
            {workout.exercise_entries.map((entry) => (
              <div 
                key={entry.id} 
                style={{ 
                  marginBottom: '12px', 
                  padding: '16px', 
                  background: 'linear-gradient(135deg, rgba(230, 213, 247, 0.15) 0%, rgba(168, 230, 207, 0.15) 100%)',
                  borderRadius: '12px',
                  border: '1px solid rgba(230, 213, 247, 0.3)',
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
            <p style={{ fontSize: '14px', color: '#666', fontStyle: 'italic', marginTop: '12px' }}>
              Note: Editing exercises and sets will be available in a future update.
            </p>
          </div>
        )}

        <div style={{ display: 'flex', gap: '12px' }}>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
          <button 
            type="button" 
            className="btn btn-secondary" 
            onClick={() => navigate('/home')}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

