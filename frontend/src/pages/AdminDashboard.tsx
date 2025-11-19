import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface MuscleGroup {
  id: number
  name: string
}

interface Exercise {
  id: number
  name: string
  primary_muscle_group_id: number
  secondary_muscle_group_ids: number[]
}

export default function AdminDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [muscleGroups, setMuscleGroups] = useState<MuscleGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingExercise, setEditingExercise] = useState<Exercise | null>(null)
  const [showMuscleGroupModal, setShowMuscleGroupModal] = useState(false)
  const [newMuscleGroupName, setNewMuscleGroupName] = useState('')
  const [creatingMuscleGroup, setCreatingMuscleGroup] = useState(false)
  const [muscleGroupError, setMuscleGroupError] = useState('')
  const [muscleGroupModalContext, setMuscleGroupModalContext] = useState<'primary' | 'secondary'>('primary')
  const [secondaryDropdownValue, setSecondaryDropdownValue] = useState('')
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    primary_muscle_group_id: '',
    secondary_muscle_group_ids: [] as number[]
  })

  useEffect(() => {
    // Check if user is superuser
    if (user && !user.is_superuser) {
      navigate('/home')
      return
    }
    fetchData()
  }, [user, navigate])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [exercisesRes, muscleGroupsRes] = await Promise.all([
        api.get('/v1/exercises?page=1&items_per_page=100'),
        api.get('/v1/muscle-groups?page=1&items_per_page=100')
      ])
      setExercises(exercisesRes.data.data || [])
      setMuscleGroups(muscleGroupsRes.data.data || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const payload = {
        name: formData.name,
        primary_muscle_group_id: parseInt(formData.primary_muscle_group_id),
        secondary_muscle_group_ids: formData.secondary_muscle_group_ids
      }

      if (editingExercise) {
        await api.patch(`/v1/exercise/${editingExercise.id}`, payload)
      } else {
        await api.post('/v1/exercise', payload)
      }

      // Reset form and refresh data
      setFormData({ name: '', primary_muscle_group_id: '', secondary_muscle_group_ids: [] })
      setShowAddForm(false)
      setEditingExercise(null)
      await fetchData()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save exercise')
    }
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this exercise?')) {
      return
    }

    try {
      await api.delete(`/v1/exercise/${id}`)
      await fetchData()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete exercise')
    }
  }

  const handleEdit = (exercise: Exercise) => {
    setEditingExercise(exercise)
    setFormData({
      name: exercise.name,
      primary_muscle_group_id: exercise.primary_muscle_group_id.toString(),
      secondary_muscle_group_ids: exercise.secondary_muscle_group_ids || []
    })
    setSecondaryDropdownValue('')
    setShowAddForm(true)
  }

  const getMuscleGroupName = (id: number) => {
    return muscleGroups.find(mg => mg.id === id)?.name || `ID: ${id}`
  }

  const handleCreateMuscleGroup = async (e: React.FormEvent) => {
    e.preventDefault()
    setMuscleGroupError('')
    setCreatingMuscleGroup(true)

    try {
      const response = await api.post('/v1/muscle-group', { name: newMuscleGroupName })
      const newMuscleGroup: MuscleGroup = {
        id: response.data.id,
        name: response.data.name
      }
      
      // Immediately add the new muscle group to the state for instant UI update
      setMuscleGroups(prev => {
        // Check if it already exists (shouldn't, but just in case)
        if (prev.find(mg => mg.id === newMuscleGroup.id)) {
          return prev
        }
        // Add to the beginning of the list
        return [newMuscleGroup, ...prev]
      })
      
      // Auto-select the newly created muscle group based on context
      if (muscleGroupModalContext === 'primary') {
        setFormData(prev => ({
          ...prev,
          primary_muscle_group_id: response.data.id.toString()
        }))
      } else {
        // Add to secondary muscle groups
        setFormData(prev => ({
          ...prev,
          secondary_muscle_group_ids: [...prev.secondary_muscle_group_ids, response.data.id]
        }))
        // Reset secondary dropdown
        setSecondaryDropdownValue('')
      }
      
      // Close modal and reset
      setShowMuscleGroupModal(false)
      setNewMuscleGroupName('')
      setMuscleGroupModalContext('primary')
      
      // Optionally refresh the full list in the background (non-blocking)
      // This ensures we have the latest data, but UI updates immediately
      api.get('/v1/muscle-groups?page=1&items_per_page=100')
        .then(muscleGroupsRes => {
          setMuscleGroups(muscleGroupsRes.data.data || [])
        })
        .catch(() => {
          // Silently fail - we already have the new group in state
        })
    } catch (err: any) {
      setMuscleGroupError(err.response?.data?.detail || 'Failed to create muscle group')
    } finally {
      setCreatingMuscleGroup(false)
    }
  }

  const handleMuscleGroupSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value
    if (value === '__create_new__') {
      // Reset dropdown to empty and show modal for primary
      setFormData({ ...formData, primary_muscle_group_id: '' })
      setMuscleGroupModalContext('primary')
      setShowMuscleGroupModal(true)
    } else {
      setFormData({ ...formData, primary_muscle_group_id: value })
    }
  }

  const handleSecondaryMuscleGroupSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value
    
    if (value === '__create_new__') {
      // Show modal for secondary
      setMuscleGroupModalContext('secondary')
      setShowMuscleGroupModal(true)
      // Reset dropdown value after opening modal
      setSecondaryDropdownValue('')
    } else if (value && value !== '') {
      // Add to secondary muscle groups if not already selected
      const id = parseInt(value, 10)
      if (!isNaN(id)) {
        setFormData(prev => {
          // Use functional update to ensure we have the latest state
          if (prev.secondary_muscle_group_ids.includes(id)) {
            // Already selected, don't add again
            return prev
          }
          // Add the new ID
          return {
            ...prev,
            secondary_muscle_group_ids: [...prev.secondary_muscle_group_ids, id]
          }
        })
      }
      // Reset dropdown to empty after selection
      setSecondaryDropdownValue('')
    }
  }

  const removeSecondaryMuscleGroup = (id: number) => {
    setFormData(prev => ({
      ...prev,
      secondary_muscle_group_ids: prev.secondary_muscle_group_ids.filter(mgId => mgId !== id)
    }))
  }

  if (loading) {
    return <div className="container">Loading...</div>
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', flexWrap: 'wrap', gap: '16px' }}>
        <h1>Admin Dashboard - Exercise Management</h1>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => navigate('/home')}>
            Back to Home
          </button>
          <button className="btn btn-secondary" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      {error && <div className="error" style={{ marginBottom: '20px' }}>{error}</div>}

      <div style={{ marginBottom: '20px' }}>
        {!showAddForm ? (
          <button className="btn btn-primary" onClick={() => setShowAddForm(true)}>
            Add New Exercise
          </button>
        ) : (
          <div className="card" style={{ marginBottom: '20px' }}>
            <h2>{editingExercise ? 'Edit Exercise' : 'Add New Exercise'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Exercise Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  maxLength={100}
                />
              </div>

              <div className="form-group">
                <label>Primary Muscle Group</label>
                <select
                  value={formData.primary_muscle_group_id}
                  onChange={handleMuscleGroupSelectChange}
                  required
                >
                  <option value="">Select a muscle group</option>
                  {muscleGroups.map(mg => (
                    <option key={mg.id} value={mg.id}>{mg.name}</option>
                  ))}
                  <option value="__create_new__" style={{ fontStyle: 'italic', color: '#666' }}>
                    + Create New Muscle Group
                  </option>
                </select>
              </div>

              <div className="form-group">
                <label>Secondary Muscle Groups (optional)</label>
                <select
                  value={secondaryDropdownValue}
                  onChange={handleSecondaryMuscleGroupSelectChange}
                  style={{ marginBottom: '12px' }}
                >
                  <option value="">Select a secondary muscle group</option>
                  {muscleGroups
                    .filter(mg => {
                      // Exclude primary muscle group and already selected secondary groups
                      const primaryId = formData.primary_muscle_group_id ? parseInt(formData.primary_muscle_group_id, 10) : null
                      const isPrimary = primaryId !== null && mg.id === primaryId
                      const isAlreadySelected = formData.secondary_muscle_group_ids.includes(mg.id)
                      return !isPrimary && !isAlreadySelected
                    })
                    .map(mg => (
                      <option key={mg.id} value={mg.id.toString()}>{mg.name}</option>
                    ))}
                  <option value="__create_new__" style={{ fontStyle: 'italic', color: '#666' }}>
                    + Create New Muscle Group
                  </option>
                </select>
                {formData.secondary_muscle_group_ids.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                    {formData.secondary_muscle_group_ids.map((id, index) => {
                      const mg = muscleGroups.find(m => m.id === id)
                      if (!mg) {
                        // If muscle group not found, show placeholder
                        return (
                          <div
                            key={`${id}-${index}`}
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '6px',
                              padding: '6px 12px',
                              background: 'linear-gradient(135deg, rgba(230, 213, 247, 0.2) 0%, rgba(168, 230, 207, 0.2) 100%)',
                              border: '1px solid rgba(230, 213, 247, 0.3)',
                              borderRadius: '8px',
                              fontSize: '14px'
                            }}
                          >
                            <span>Loading...</span>
                            <button
                              type="button"
                              onClick={() => removeSecondaryMuscleGroup(id)}
                              style={{
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '18px',
                                lineHeight: '1',
                                padding: '0',
                                color: '#666',
                                fontWeight: 'bold'
                              }}
                              title="Remove"
                            >
                              ×
                            </button>
                          </div>
                        )
                      }
                      return (
                        <div
                          key={`${id}-${mg.name}`}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '6px 12px',
                            background: 'linear-gradient(135deg, rgba(230, 213, 247, 0.2) 0%, rgba(168, 230, 207, 0.2) 100%)',
                            border: '1px solid rgba(230, 213, 247, 0.3)',
                            borderRadius: '8px',
                            fontSize: '14px'
                          }}
                        >
                          <span>{mg.name}</span>
                          <button
                            type="button"
                            onClick={() => removeSecondaryMuscleGroup(id)}
                            style={{
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              fontSize: '18px',
                              lineHeight: '1',
                              padding: '0',
                              color: '#666',
                              fontWeight: 'bold'
                            }}
                            title="Remove"
                          >
                            ×
                          </button>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button type="submit" className="btn btn-primary">
                  {editingExercise ? 'Update Exercise' : 'Create Exercise'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowAddForm(false)
                    setEditingExercise(null)
                    setFormData({ name: '', primary_muscle_group_id: '', secondary_muscle_group_ids: [] })
                    setSecondaryDropdownValue('')
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Create Muscle Group Modal */}
      {showMuscleGroupModal && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(4px)'
          }}
          onClick={() => {
            setShowMuscleGroupModal(false)
            setNewMuscleGroupName('')
            setMuscleGroupError('')
            setMuscleGroupModalContext('primary')
            // Reset secondary dropdown if modal was opened from secondary
            if (muscleGroupModalContext === 'secondary') {
              setSecondaryDropdownValue('')
            }
          }}
        >
          <div 
            className="card" 
            style={{ 
              maxWidth: '400px', 
              width: '90%',
              margin: '20px',
              position: 'relative'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{ marginBottom: '20px' }}>Create New Muscle Group</h2>
            <form onSubmit={handleCreateMuscleGroup}>
              <div className="form-group">
                <label>Muscle Group Name</label>
                <input
                  type="text"
                  value={newMuscleGroupName}
                  onChange={(e) => setNewMuscleGroupName(e.target.value)}
                  required
                  maxLength={50}
                  autoFocus
                  placeholder="e.g., Chest, Back, Legs"
                />
              </div>
              {muscleGroupError && <div className="error">{muscleGroupError}</div>}
              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={creatingMuscleGroup}
                >
                  {creatingMuscleGroup ? 'Creating...' : 'Create Muscle Group'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowMuscleGroupModal(false)
                    setNewMuscleGroupName('')
                    setMuscleGroupError('')
                    const wasSecondary = muscleGroupModalContext === 'secondary'
                    setMuscleGroupModalContext('primary')
                    // Reset secondary dropdown if modal was opened from secondary
                    if (wasSecondary) {
                      setSecondaryDropdownValue('')
                    }
                  }}
                  disabled={creatingMuscleGroup}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="card">
        <h2>Exercises ({exercises.length})</h2>
        {exercises.length === 0 ? (
          <p style={{ textAlign: 'center', padding: '40px' }}>
            No exercises found. Create your first exercise above.
          </p>
        ) : (
          <div style={{ display: 'grid', gap: '16px' }}>
            {exercises.map(exercise => (
              <div
                key={exercise.id}
                style={{
                  padding: '20px',
                  background: 'linear-gradient(135deg, rgba(230, 213, 247, 0.12) 0%, rgba(168, 230, 207, 0.12) 100%)',
                  border: '1px solid rgba(230, 213, 247, 0.3)',
                  borderRadius: '12px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
                  color: '#1A1A1A'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)'
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(230, 213, 247, 0.2)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.05)'
                }}
              >
                <div>
                  <h3 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>{exercise.name}</h3>
                  <p style={{ margin: '0', fontSize: '14px' }}>
                    Primary: <strong>{getMuscleGroupName(exercise.primary_muscle_group_id)}</strong>
                    {exercise.secondary_muscle_group_ids && exercise.secondary_muscle_group_ids.length > 0 && (
                      <span style={{ marginLeft: '15px' }}>
                        Secondary: {exercise.secondary_muscle_group_ids.map(id => getMuscleGroupName(id)).join(', ')}
                      </span>
                    )}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    className="btn btn-secondary"
                    onClick={() => handleEdit(exercise)}
                    style={{ fontSize: '14px', padding: '8px 16px' }}
                  >
                    Edit
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDelete(exercise.id)}
                    style={{ fontSize: '14px', padding: '8px 16px' }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

