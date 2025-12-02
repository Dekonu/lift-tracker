import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import api from '../services/api'
import { useExercises } from '../contexts/ExercisesContext'

interface Exercise {
  id: number
  name: string
  primary_muscle_group_ids: number[]
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
  reps?: number
}

export default function CreateWorkout() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { exercises, loading: exercisesLoading, error: exercisesError } = useExercises()
  const [selectedExercises, setSelectedExercises] = useState<ExerciseInstance[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  
  // Get date from URL or use current date/time
  const getInitialDate = () => {
    const dateParam = searchParams.get('date')
    if (dateParam) {
      // If date is provided, set time to current time
      const date = new Date(dateParam)
      const now = new Date()
      date.setHours(now.getHours())
      date.setMinutes(now.getMinutes())
      return date
    }
    return new Date()
  }
  
  const [workoutDate, setWorkoutDate] = useState<Date>(getInitialDate())

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
      // Create workout session with selected date
      const sessionResponse = await api.post('/v1/workout-session', {
        started_at: workoutDate.toISOString(),
        name: null // Will be auto-generated
      })

      const sessionId = sessionResponse.data.id

      // Add exercise entries and sets
      for (let i = 0; i < selectedExercises.length; i++) {
        const exerciseInstance = selectedExercises[i]
        const entryResponse = await api.post(`/v1/workout-session/${sessionId}/exercise-entry`, {
          workout_session_id: sessionId,
          exercise_id: exerciseInstance.exercise_id,
          order: exerciseInstance.order
        })

        const exerciseEntryId = entryResponse.data.id

        // Add sets
        for (let setIndex = 0; setIndex < exerciseInstance.sets.length; setIndex++) {
          const set = exerciseInstance.sets[setIndex]
          // Convert weight to kg if needed
          let weight_kg: number | null = null
          if (set.weight_type === 'static') {
            if (set.unit === 'kg') {
              weight_kg = set.weight_value
            } else if (set.unit === 'lbs') {
              weight_kg = set.weight_value * 0.453592 // Convert lbs to kg
            }
          }

          const setEntry = {
            exercise_entry_id: exerciseEntryId,
            set_number: setIndex + 1, // 1-indexed
            weight_kg: weight_kg,
            reps: set.reps || null,
            rir: set.rir || null,
            percentage_of_1rm: set.weight_type === 'percentage' ? set.weight_value : null,
            rest_seconds: set.rest_time_seconds || null,
            notes: set.notes || null,
            is_warmup: false
          }

          await api.post(`/v1/exercise-entry/${exerciseEntryId}/set`, setEntry)
        }
      }

      // Navigate to home with the workout date selected
      const workoutDateStr = workoutDate.toISOString().split('T')[0]
      // Use replace: false to allow the Home component to handle the date parameter
      navigate(`/home?date=${workoutDateStr}`, { replace: false })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create workout')
    } finally {
      setSaving(false)
    }
  }

  if (exercisesLoading) {
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

      {(error || exercisesError) && (
        <div className="error" style={{ marginBottom: '20px' }}>
          {error || exercisesError}
        </div>
      )}

      {!exercisesLoading && exercises.length === 0 && !exercisesError && (
        <div className="error" style={{ marginBottom: '20px' }}>
          No exercises available. Please create exercises first or sync from Wger API in the admin dashboard.
        </div>
      )}

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

