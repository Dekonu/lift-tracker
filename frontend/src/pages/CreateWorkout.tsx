import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

interface Exercise {
  id: number
  name: string
  primary_muscle_group_id: number
}

interface ExerciseInstance {
  exercise_id: number
  order: number
  sets: SetData[]
}

interface SetData {
  weight_value: number
  weight_type: 'percentage' | 'static'
  unit: 'lbs' | 'kg'
  rest_time_seconds?: number
  rir?: number
  notes?: string
}

export default function CreateWorkout() {
  const navigate = useNavigate()
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [selectedExercises, setSelectedExercises] = useState<ExerciseInstance[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchExercises()
  }, [])

  const fetchExercises = async () => {
    try {
      const response = await api.get('/v1/exercises?page=1&items_per_page=100')
      setExercises(response.data.data || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch exercises')
    } finally {
      setLoading(false)
    }
  }

  const addExercise = () => {
    if (exercises.length === 0) {
      setError('No exercises available. Please create exercises first.')
      return
    }
    setSelectedExercises([
      ...selectedExercises,
      {
        exercise_id: exercises[0].id,
        order: selectedExercises.length,
        sets: []
      }
    ])
  }

  const removeExercise = (index: number) => {
    setSelectedExercises(selectedExercises.filter((_, i) => i !== index).map((ei, i) => ({ ...ei, order: i })))
  }

  const updateExercise = (index: number, exercise_id: number) => {
    const updated = [...selectedExercises]
    updated[index].exercise_id = exercise_id
    setSelectedExercises(updated)
  }

  const addSet = (exerciseIndex: number) => {
    const updated = [...selectedExercises]
    updated[exerciseIndex].sets.push({
      weight_value: 0,
      weight_type: 'static',
      unit: 'lbs'
    })
    setSelectedExercises(updated)
  }

  const removeSet = (exerciseIndex: number, setIndex: number) => {
    const updated = [...selectedExercises]
    updated[exerciseIndex].sets.splice(setIndex, 1)
    setSelectedExercises(updated)
  }

  const updateSet = (exerciseIndex: number, setIndex: number, field: keyof SetData, value: any) => {
    const updated = [...selectedExercises]
    updated[exerciseIndex].sets[setIndex] = {
      ...updated[exerciseIndex].sets[setIndex],
      [field]: value
    }
    setSelectedExercises(updated)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSaving(true)

    try {
      // Create workout
      const workoutResponse = await api.post('/v1/workout', {
        date: new Date().toISOString()
      })

      const workoutId = workoutResponse.data.id

      // Add exercise instances and sets
      for (const exerciseInstance of selectedExercises) {
        const eiResponse = await api.post(`/v1/workout/${workoutId}/exercise-instance`, {
          exercise_id: exerciseInstance.exercise_id,
          order: exerciseInstance.order
        })

        const exerciseInstanceId = eiResponse.data.id

        // Add sets
        for (const set of exerciseInstance.sets) {
          await api.post(`/v1/exercise-instance/${exerciseInstanceId}/set`, set)
        }
      }

      navigate('/home')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create workout')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="container">Loading exercises...</div>
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Create Workout</h1>
        <button className="btn btn-secondary" onClick={() => navigate('/home')}>
          Cancel
        </button>
      </div>

      {error && <div className="error" style={{ marginBottom: '20px' }}>{error}</div>}

      <form onSubmit={handleSubmit}>
        {selectedExercises.map((exerciseInstance, exerciseIndex) => (
          <div key={exerciseIndex} className="card" style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h3>Exercise {exerciseIndex + 1}</h3>
              <button
                type="button"
                className="btn btn-danger"
                onClick={() => removeExercise(exerciseIndex)}
              >
                Remove
              </button>
            </div>

            <div className="form-group">
              <label>Exercise</label>
              <select
                value={exerciseInstance.exercise_id}
                onChange={(e) => updateExercise(exerciseIndex, parseInt(e.target.value))}
                required
              >
                {exercises.map((exercise) => (
                  <option key={exercise.id} value={exercise.id}>
                    {exercise.name}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ marginTop: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h4>Sets</h4>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => addSet(exerciseIndex)}
                >
                  Add Set
                </button>
              </div>

              {exerciseInstance.sets.map((set, setIndex) => (
                <div key={setIndex} style={{ padding: '15px', background: '#f9f9f9', borderRadius: '5px', marginBottom: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <strong>Set {setIndex + 1}</strong>
                    <button
                      type="button"
                      className="btn btn-danger"
                      style={{ padding: '5px 10px', fontSize: '14px' }}
                      onClick={() => removeSet(exerciseIndex, setIndex)}
                    >
                      Remove
                    </button>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    <div className="form-group">
                      <label>Weight Value</label>
                      <input
                        type="number"
                        step="0.1"
                        value={set.weight_value}
                        onChange={(e) => updateSet(exerciseIndex, setIndex, 'weight_value', parseFloat(e.target.value))}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Weight Type</label>
                      <select
                        value={set.weight_type}
                        onChange={(e) => updateSet(exerciseIndex, setIndex, 'weight_type', e.target.value)}
                        required
                      >
                        <option value="static">Static</option>
                        <option value="percentage">Percentage of 1RM</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Unit</label>
                      <select
                        value={set.unit}
                        onChange={(e) => updateSet(exerciseIndex, setIndex, 'unit', e.target.value)}
                        required
                      >
                        <option value="lbs">lbs</option>
                        <option value="kg">kg</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Rest Time (seconds)</label>
                      <input
                        type="number"
                        value={set.rest_time_seconds || ''}
                        onChange={(e) => updateSet(exerciseIndex, setIndex, 'rest_time_seconds', e.target.value ? parseInt(e.target.value) : undefined)}
                      />
                    </div>
                    <div className="form-group">
                      <label>RIR (Reps in Reserve)</label>
                      <input
                        type="number"
                        value={set.rir || ''}
                        onChange={(e) => updateSet(exerciseIndex, setIndex, 'rir', e.target.value ? parseInt(e.target.value) : undefined)}
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Notes</label>
                    <textarea
                      value={set.notes || ''}
                      onChange={(e) => updateSet(exerciseIndex, setIndex, 'notes', e.target.value)}
                      rows={2}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        <div style={{ marginBottom: '20px' }}>
          <button
            type="button"
            className="btn btn-primary"
            onClick={addExercise}
          >
            Add Exercise
          </button>
        </div>

        {selectedExercises.length > 0 && (
          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '15px', fontSize: '18px' }}
            disabled={saving}
          >
            {saving ? 'Creating Workout...' : 'Create Workout'}
          </button>
        )}
      </form>
    </div>
  )
}

