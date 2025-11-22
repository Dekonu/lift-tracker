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
  primary_muscle_group_ids: number[]
  secondary_muscle_group_ids: number[]
  enabled: boolean
}

export default function ExerciseManagement() {
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
  const [primaryDropdownValue, setPrimaryDropdownValue] = useState('')
  const [secondaryDropdownValue, setSecondaryDropdownValue] = useState('')
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<{created: number, updated: number, skipped: number, errors: string[]} | null>(null)
  const [wgerSyncMode, setWgerSyncMode] = useState<'partial' | 'full'>('partial')
  const [wgerSyncing, setWgerSyncing] = useState(false)
  const [wgerSyncResult, setWgerSyncResult] = useState<{created: number, updated: number, skipped: number, muscle_groups_created: number, errors: string[]} | null>(null)
  
  // Filter state
  const [filterName, setFilterName] = useState('')
  const [filterMuscleGroup, setFilterMuscleGroup] = useState<number | ''>('')
  const [filterEnabled, setFilterEnabled] = useState<'all' | 'enabled' | 'disabled'>('all')
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    primary_muscle_group_ids: [] as number[],
    secondary_muscle_group_ids: [] as number[],
    enabled: true
  })

  useEffect(() => {
    // Check if user is superuser
    if (!user?.is_superuser) {
      navigate('/home')
      return
    }
    fetchExercises()
    fetchMuscleGroups()
  }, [user, navigate])

  async function fetchExercises() {
    try {
      setLoading(true)
      const response = await api.get('/v1/exercises?items_per_page=1000')
      const exercisesData = response.data.data || []
      setExercises(exercisesData)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch exercises')
    } finally {
      setLoading(false)
    }
  }

  async function fetchMuscleGroups() {
    try {
      const response = await api.get('/v1/muscle-groups?items_per_page=1000')
      const muscleGroupsData = response.data.data || []
      setMuscleGroups(muscleGroupsData)
    } catch (err: any) {
      console.error('Failed to fetch muscle groups:', err)
    }
  }

  function getFilteredExercises(): Exercise[] {
    return exercises.filter(exercise => {
      // Filter by name
      if (filterName && !exercise.name.toLowerCase().includes(filterName.toLowerCase())) {
        return false
      }
      
      // Filter by muscle group
      if (filterMuscleGroup !== '') {
        const hasMuscleGroup = exercise.primary_muscle_group_ids.includes(filterMuscleGroup as number) ||
                               exercise.secondary_muscle_group_ids.includes(filterMuscleGroup as number)
        if (!hasMuscleGroup) {
          return false
        }
      }
      
      // Filter by enabled status
      if (filterEnabled === 'enabled' && !exercise.enabled) {
        return false
      }
      if (filterEnabled === 'disabled' && exercise.enabled) {
        return false
      }
      
      return true
    })
  }

  function getMuscleGroupName(id: number): string {
    const mg = muscleGroups.find(m => m.id === id)
    return mg ? mg.name : `ID:${id}`
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (editingExercise) {
        await api.patch(`/v1/exercise/${editingExercise.id}`, {
          name: formData.name,
          primary_muscle_group_ids: formData.primary_muscle_group_ids,
          secondary_muscle_group_ids: formData.secondary_muscle_group_ids,
          enabled: formData.enabled
        })
      } else {
        await api.post('/v1/exercise', {
          name: formData.name,
          primary_muscle_group_ids: formData.primary_muscle_group_ids,
          secondary_muscle_group_ids: formData.secondary_muscle_group_ids,
          enabled: formData.enabled
        })
      }
      setFormData({
        name: '',
        primary_muscle_group_ids: [],
        secondary_muscle_group_ids: [],
        enabled: true
      })
      setPrimaryDropdownValue('')
      setSecondaryDropdownValue('')
      setShowAddForm(false)
      setEditingExercise(null)
      await fetchExercises()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save exercise')
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm('Are you sure you want to delete this exercise?')) {
      return
    }
    try {
      await api.delete(`/v1/exercise/${id}`)
      await fetchExercises()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete exercise')
    }
  }

  function handleEdit(exercise: Exercise) {
    setEditingExercise(exercise)
    setFormData({
      name: exercise.name,
      primary_muscle_group_ids: exercise.primary_muscle_group_ids || [],
      secondary_muscle_group_ids: exercise.secondary_muscle_group_ids || [],
      enabled: exercise.enabled
    })
    setPrimaryDropdownValue('')
    setSecondaryDropdownValue('')
    setShowAddForm(true)
  }

  async function handleToggleEnabled(exercise: Exercise) {
    try {
      await api.patch(`/v1/exercise/${exercise.id}`, {
        enabled: !exercise.enabled
      })
      await fetchExercises()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to toggle exercise status')
    }
  }

  async function handleCreateMuscleGroup() {
    if (!newMuscleGroupName.trim()) {
      setMuscleGroupError('Muscle group name is required')
      return
    }
    
    try {
      setCreatingMuscleGroup(true)
      setMuscleGroupError('')
      const response = await api.post('/v1/muscle-group', {
        name: newMuscleGroupName.trim()
      })
      
      const newMuscleGroup = response.data
      await fetchMuscleGroups()
      
      // Immediately add the new muscle group to the state for instant UI update
      setMuscleGroups(prev => [...prev, newMuscleGroup])
      
      // Auto-select the newly created muscle group based on context
      if (muscleGroupModalContext === 'primary') {
        if (!formData.primary_muscle_group_ids.includes(newMuscleGroup.id)) {
          setFormData(prev => ({
            ...prev,
            primary_muscle_group_ids: [...prev.primary_muscle_group_ids, newMuscleGroup.id]
          }))
        }
        setPrimaryDropdownValue('')
      } else {
        // Add to secondary muscle groups
        if (!formData.secondary_muscle_group_ids.includes(newMuscleGroup.id)) {
          setFormData(prev => ({
            ...prev,
            secondary_muscle_group_ids: [...prev.secondary_muscle_group_ids, newMuscleGroup.id]
          }))
        }
        // Reset secondary dropdown
        setSecondaryDropdownValue('')
      }
      
      setNewMuscleGroupName('')
      setShowMuscleGroupModal(false)
    } catch (err: any) {
      setMuscleGroupError(err.response?.data?.detail || 'Failed to create muscle group')
    } finally {
      setCreatingMuscleGroup(false)
    }
  }

  function handlePrimaryMuscleGroupSelectChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const value = e.target.value
    setPrimaryDropdownValue('')
    
    if (value === '__create_new__') {
      setMuscleGroupModalContext('primary')
      setShowMuscleGroupModal(true)
      return
    }
    
    if (value && value !== '') {
      const id = parseInt(value, 10)
      // Add to primary muscle groups if not already selected
      if (!formData.primary_muscle_group_ids.includes(id)) {
        setFormData(prev => ({
          ...prev,
          primary_muscle_group_ids: [...prev.primary_muscle_group_ids, id]
        }))
      }
      // Reset dropdown to empty after selection
      setPrimaryDropdownValue('')
    }
  }

  function removePrimaryMuscleGroup(id: number) {
    setFormData(prev => ({
      ...prev,
      primary_muscle_group_ids: prev.primary_muscle_group_ids.filter(mgId => mgId !== id)
    }))
  }

  function handleSecondaryMuscleGroupSelectChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const value = e.target.value
    // Reset dropdown value after opening modal
    setSecondaryDropdownValue('')
    
    if (value === '__create_new__') {
      setMuscleGroupModalContext('secondary')
      setShowMuscleGroupModal(true)
      // Reset dropdown value after opening modal
      setSecondaryDropdownValue('')
      return
    }
    
    if (value && value !== '') {
      const id = parseInt(value, 10)
      // Add to secondary muscle groups if not already selected
      if (!formData.secondary_muscle_group_ids.includes(id)) {
        setFormData(prev => ({
          ...prev,
          secondary_muscle_group_ids: [...prev.secondary_muscle_group_ids, id]
        }))
      }
      // Reset dropdown to empty after selection
      setSecondaryDropdownValue('')
    }
  }

  function removeSecondaryMuscleGroup(id: number) {
    setFormData(prev => ({
      ...prev,
      secondary_muscle_group_ids: prev.secondary_muscle_group_ids.filter(mgId => mgId !== id)
    }))
  }

  async function handleExport() {
    try {
      const response = await api.get('/v1/exercises/export', {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'exercises_export.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to export exercises')
    }
  }

  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    
    try {
      setImporting(true)
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post('/v1/exercises/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      setImportResult(response.data)
      await fetchExercises()
      // Reset file input
      e.target.value = ''
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import exercises')
    } finally {
      setImporting(false)
    }
  }

  async function handleWgerSync() {
    try {
      setWgerSyncing(true)
      const response = await api.post(`/v1/exercises/sync-wger?full_sync=${wgerSyncMode === 'full'}`)
      setWgerSyncResult(response.data)
      await fetchExercises()
      await fetchMuscleGroups()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync with Wger')
    } finally {
      setWgerSyncing(false)
    }
  }

  if (loading) {
    return <div className="container">Loading...</div>
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', flexWrap: 'wrap', gap: '16px' }}>
        <h1>Exercise Management</h1>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => navigate('/admin')}>
            Back to Dashboard
          </button>
          <button className="btn btn-secondary" onClick={() => navigate('/home')}>
            Back to Home
          </button>
          <button className="btn btn-secondary" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      {error && <div className="error" style={{ marginBottom: '20px' }}>{error}</div>}
      
      {importResult && (
        <div style={{ 
          marginBottom: '20px', 
          padding: '15px', 
          background: 'linear-gradient(135deg, rgba(168, 230, 207, 0.2) 0%, rgba(230, 213, 247, 0.2) 100%)',
          border: '1px solid rgba(168, 230, 207, 0.3)',
          borderRadius: '8px'
        }}>
          <h3 style={{ margin: '0 0 10px 0' }}>Import Results</h3>
          <p style={{ margin: '5px 0' }}>✅ Created: {importResult.created}</p>
          <p style={{ margin: '5px 0' }}>🔄 Updated: {importResult.updated}</p>
          <p style={{ margin: '5px 0' }}>⏭️ Skipped: {importResult.skipped}</p>
          {importResult.errors.length > 0 && (
            <div style={{ marginTop: '10px' }}>
              <strong>Errors:</strong>
              <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                {importResult.errors.map((err: string, idx: number) => (
                  <li key={idx} style={{ color: '#d32f2f' }}>{err}</li>
                ))}
              </ul>
            </div>
          )}
          <button 
            className="btn btn-secondary" 
            onClick={() => setImportResult(null)}
            style={{ marginTop: '10px' }}
          >
            Dismiss
          </button>
        </div>
      )}

      {wgerSyncResult && (
        <div style={{ 
          marginBottom: '20px', 
          padding: '15px', 
          background: 'linear-gradient(135deg, rgba(168, 230, 207, 0.2) 0%, rgba(230, 213, 247, 0.2) 100%)',
          border: '1px solid rgba(168, 230, 207, 0.3)',
          borderRadius: '8px'
        }}>
          <h3 style={{ margin: '0 0 10px 0' }}>Wger Sync Results</h3>
          <p style={{ margin: '5px 0' }}>✅ Created: {wgerSyncResult.created}</p>
          <p style={{ margin: '5px 0' }}>🔄 Updated: {wgerSyncResult.updated}</p>
          <p style={{ margin: '5px 0' }}>⏭️ Skipped: {wgerSyncResult.skipped}</p>
          <p style={{ margin: '5px 0' }}>💪 Muscle Groups Created: {wgerSyncResult.muscle_groups_created}</p>
          {wgerSyncResult.errors.length > 0 && (
            <div style={{ marginTop: '10px' }}>
              <strong>Errors:</strong>
              <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                {wgerSyncResult.errors.map((err: string, idx: number) => (
                  <li key={idx} style={{ color: '#d32f2f' }}>{err}</li>
                ))}
              </ul>
            </div>
          )}
          <button 
            className="btn btn-secondary" 
            onClick={() => setWgerSyncResult(null)}
            style={{ marginTop: '10px' }}
          >
            Dismiss
          </button>
        </div>
      )}

      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
          <button 
            className="btn btn-primary" 
            onClick={() => {
              setShowAddForm(!showAddForm)
              setEditingExercise(null)
              setFormData({
                name: '',
                primary_muscle_group_ids: [],
                secondary_muscle_group_ids: [],
                enabled: true
              })
              setPrimaryDropdownValue('')
              setSecondaryDropdownValue('')
            }}
          >
            {showAddForm ? 'Cancel' : 'Add Exercise'}
          </button>
          <button className="btn btn-secondary" onClick={handleExport}>
            📥 Export CSV
          </button>
          <label className="btn btn-secondary" style={{ cursor: 'pointer', margin: 0 }}>
            📤 Import CSV
            <input
              type="file"
              accept=".csv"
              onChange={handleImport}
              style={{ display: 'none' }}
              disabled={importing}
            />
          </label>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            padding: '8px 12px',
            background: 'rgba(255, 255, 255, 0.6)',
            border: '1px solid rgba(230, 213, 247, 0.4)',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
            marginLeft: '4px'
          }}>
            <span style={{ 
              fontSize: '13px', 
              fontWeight: '600', 
              color: '#4A4A4A',
              marginRight: '4px'
            }}>
              Wger Sync Mode:
            </span>
            <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', fontSize: '13px' }}>
              <input
                type="radio"
                name="wgerSyncMode"
                value="partial"
                checked={wgerSyncMode === 'partial'}
                onChange={(e) => setWgerSyncMode(e.target.value as 'partial' | 'full')}
                style={{ margin: 0, cursor: 'pointer' }}
              />
              <span>Partial</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', fontSize: '13px' }}>
              <input
                type="radio"
                name="wgerSyncMode"
                value="full"
                checked={wgerSyncMode === 'full'}
                onChange={(e) => setWgerSyncMode(e.target.value as 'partial' | 'full')}
                style={{ margin: 0, cursor: 'pointer' }}
              />
              <span>Full</span>
            </label>
            <button 
              className="btn btn-secondary" 
              onClick={handleWgerSync}
              disabled={wgerSyncing}
              title="Sync exercises from Wger API"
              style={{ 
                padding: '8px 16px', 
                fontSize: '13px',
                marginLeft: '2px'
              }}
            >
              {wgerSyncing ? 'Syncing...' : '🔄 Sync'}
            </button>
          </div>
          {(importing || wgerSyncing) && (
            <span style={{ 
              fontSize: '13px', 
              color: '#666',
              fontStyle: 'italic',
              marginLeft: '8px',
              whiteSpace: 'nowrap'
            }}>
              {importing ? 'Importing...' : wgerSyncing ? 'Syncing...' : ''}
            </span>
          )}
        </div>
      </div>

      {showAddForm ? (
        <div>
          {editingExercise ? (
            <div className="card" style={{ marginBottom: '20px' }}>
              <h2>Edit Exercise</h2>
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
                  <label>Primary Muscle Groups (at least one required)</label>
                  <select
                    value={primaryDropdownValue}
                    onChange={handlePrimaryMuscleGroupSelectChange}
                    style={{ 
                      marginBottom: '12px',
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid rgba(0, 0, 0, 0.1)',
                      borderRadius: '6px',
                      fontSize: '14px',
                      background: 'white'
                    }}
                  >
                    <option value="">Select a primary muscle group</option>
                    {muscleGroups
                      .filter(mg => {
                        // Exclude already selected primary groups
                        const isAlreadySelected = formData.primary_muscle_group_ids.includes(mg.id)
                        return !isAlreadySelected
                      })
                      .map(mg => (
                        <option key={mg.id} value={mg.id.toString()}>{mg.name}</option>
                      ))}
                    <option value="__create_new__" style={{ fontStyle: 'italic', color: '#666' }}>
                      + Create New Muscle Group
                    </option>
                  </select>
                  {formData.primary_muscle_group_ids.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                      {formData.primary_muscle_group_ids.map((id, index) => {
                        const mg = muscleGroups.find(m => m.id === id)
                        if (!mg) {
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
                                onClick={() => removePrimaryMuscleGroup(id)}
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
                              >
                                ×
                              </button>
                            </div>
                          )
                        }
                        return (
                          <div
                            key={mg.id}
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
                              onClick={() => removePrimaryMuscleGroup(mg.id)}
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
                            >
                              ×
                            </button>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label>Secondary Muscle Groups (optional)</label>
                  <select
                    value={secondaryDropdownValue}
                    onChange={handleSecondaryMuscleGroupSelectChange}
                    style={{ 
                      marginBottom: '12px',
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid rgba(0, 0, 0, 0.1)',
                      borderRadius: '6px',
                      fontSize: '14px',
                      background: 'white'
                    }}
                  >
                    <option value="">Select a secondary muscle group</option>
                    {muscleGroups
                      .filter(mg => {
                        // Exclude primary muscle groups and already selected secondary groups
                        const isPrimary = formData.primary_muscle_group_ids.includes(mg.id)
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
                              >
                                ×
                              </button>
                            </div>
                          )
                        }
                        // If muscle group not found, show placeholder
                        return (
                          <div
                            key={mg.id}
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
                              onClick={() => removeSecondaryMuscleGroup(mg.id)}
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
                            >
                              ×
                            </button>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="checkbox"
                      checked={formData.enabled}
                      onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                    />
                    <span>Enabled</span>
                  </label>
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                  <button type="submit" className="btn btn-primary">
                    Update Exercise
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-secondary" 
                    onClick={() => {
                      setShowAddForm(false)
                      setEditingExercise(null)
                      setFormData({
                        name: '',
                        primary_muscle_group_ids: [],
                        secondary_muscle_group_ids: [],
                        enabled: true
                      })
                      setPrimaryDropdownValue('')
                      setSecondaryDropdownValue('')
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          ) : (
            <div className="card" style={{ marginBottom: '20px' }}>
              <h2>Add New Exercise</h2>
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
                  <label>Primary Muscle Groups (at least one required)</label>
                  <select
                    value={primaryDropdownValue}
                    onChange={handlePrimaryMuscleGroupSelectChange}
                    style={{ 
                      marginBottom: '12px',
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid rgba(0, 0, 0, 0.1)',
                      borderRadius: '6px',
                      fontSize: '14px',
                      background: 'white'
                    }}
                  >
                    <option value="">Select a primary muscle group</option>
                    {muscleGroups
                      .filter(mg => {
                        // Exclude already selected primary groups
                        const isAlreadySelected = formData.primary_muscle_group_ids.includes(mg.id)
                        return !isAlreadySelected
                      })
                      .map(mg => (
                        <option key={mg.id} value={mg.id.toString()}>{mg.name}</option>
                      ))}
                    <option value="__create_new__" style={{ fontStyle: 'italic', color: '#666' }}>
                      + Create New Muscle Group
                    </option>
                  </select>
                  {formData.primary_muscle_group_ids.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                      {formData.primary_muscle_group_ids.map((id, index) => {
                        const mg = muscleGroups.find(m => m.id === id)
                        if (!mg) {
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
                                onClick={() => removePrimaryMuscleGroup(id)}
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
                              >
                                ×
                              </button>
                            </div>
                          )
                        }
                        return (
                          <div
                            key={mg.id}
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
                              onClick={() => removePrimaryMuscleGroup(mg.id)}
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
                            >
                              ×
                            </button>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label>Secondary Muscle Groups (optional)</label>
                  <select
                    value={secondaryDropdownValue}
                    onChange={handleSecondaryMuscleGroupSelectChange}
                    style={{ 
                      marginBottom: '12px',
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid rgba(0, 0, 0, 0.1)',
                      borderRadius: '6px',
                      fontSize: '14px',
                      background: 'white'
                    }}
                  >
                    <option value="">Select a secondary muscle group</option>
                    {muscleGroups
                      .filter(mg => {
                        // Exclude primary muscle groups and already selected secondary groups
                        const isPrimary = formData.primary_muscle_group_ids.includes(mg.id)
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
                              >
                                ×
                              </button>
                            </div>
                          )
                        }
                        // If muscle group not found, show placeholder
                        return (
                          <div
                            key={mg.id}
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
                              onClick={() => removeSecondaryMuscleGroup(mg.id)}
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
                            >
                              ×
                            </button>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="checkbox"
                      checked={formData.enabled}
                      onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                    />
                    <span>Enabled</span>
                  </label>
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                  <button type="submit" className="btn btn-primary">
                    Create Exercise
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-secondary" 
                    onClick={() => {
                      setShowAddForm(false)
                      setFormData({
                        name: '',
                        primary_muscle_group_ids: [],
                        secondary_muscle_group_ids: [],
                        enabled: true
                      })
                      setPrimaryDropdownValue('')
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
      ) : null}

      {/* Create Muscle Group Modal */}
      {showMuscleGroupModal && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowMuscleGroupModal(false)
              setNewMuscleGroupName('')
              setMuscleGroupError('')
              // Reset secondary dropdown if modal was opened from secondary
              if (muscleGroupModalContext === 'secondary') {
                setSecondaryDropdownValue('')
              }
            }
          }}
        >
          <div className="card" style={{ maxWidth: '500px', width: '90%', position: 'relative' }}>
            <h2 style={{ marginBottom: '20px' }}>Create New Muscle Group</h2>
            <form onSubmit={(e) => { e.preventDefault(); handleCreateMuscleGroup(); }}>
              <div className="form-group">
                <label>Muscle Group Name</label>
                <input
                  type="text"
                  value={newMuscleGroupName}
                  onChange={(e) => setNewMuscleGroupName(e.target.value)}
                  required
                  maxLength={50}
                  autoFocus
                />
                {muscleGroupError && (
                  <div className="error" style={{ marginTop: '8px' }}>{muscleGroupError}</div>
                )}
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button type="submit" className="btn btn-primary" disabled={creatingMuscleGroup}>
                  {creatingMuscleGroup ? 'Creating...' : 'Create Muscle Group'}
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => {
                    setShowMuscleGroupModal(false)
                    setNewMuscleGroupName('')
                    setMuscleGroupError('')
                    // Reset secondary dropdown if modal was opened from secondary
                    if (muscleGroupModalContext === 'secondary') {
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

      <div className="card" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 200px)', minHeight: '600px' }}>
        <div style={{ flexShrink: 0 }}>
          <h2 style={{ marginBottom: '20px' }}>Exercises ({exercises.length}) {getFilteredExercises().length !== exercises.length && `(Filtered: ${getFilteredExercises().length})`}</h2>
        
          {/* Filter Controls */}
          <div style={{ 
            marginBottom: '20px', 
            padding: '16px', 
            background: 'rgba(255, 255, 255, 0.5)', 
            borderRadius: '8px',
            display: 'flex',
            flexWrap: 'wrap',
            gap: '12px',
            alignItems: 'flex-end'
          }}>
            <div style={{ flex: '1', minWidth: '200px' }}>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: 600, color: '#4A4A4A' }}>
                Filter by Name
              </label>
              <input
                type="text"
                placeholder="Search exercise name..."
                value={filterName}
                onChange={(e) => setFilterName(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid rgba(0, 0, 0, 0.1)',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              />
            </div>
            
            <div style={{ flex: '1', minWidth: '200px' }}>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: 600, color: '#4A4A4A' }}>
                Filter by Muscle Group
              </label>
              <select
                value={filterMuscleGroup}
                onChange={(e) => setFilterMuscleGroup(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid rgba(0, 0, 0, 0.1)',
                  borderRadius: '6px',
                  fontSize: '14px',
                  background: 'white'
                }}
              >
                <option value="">All Muscle Groups</option>
                {muscleGroups.map(mg => (
                  <option key={mg.id} value={mg.id}>{mg.name}</option>
                ))}
              </select>
            </div>
            
            <div style={{ flex: '1', minWidth: '150px' }}>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: 600, color: '#4A4A4A' }}>
                Filter by Status
              </label>
              <select
                value={filterEnabled}
                onChange={(e) => setFilterEnabled(e.target.value as 'all' | 'enabled' | 'disabled')}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid rgba(0, 0, 0, 0.1)',
                  borderRadius: '6px',
                  fontSize: '14px',
                  background: 'white'
                }}
              >
                <option value="all">All Exercises</option>
                <option value="enabled">Enabled Only</option>
                <option value="disabled">Disabled Only</option>
              </select>
            </div>
            
            {(filterName || filterMuscleGroup !== '' || filterEnabled !== 'all') && (
              <button
                type="button"
                onClick={() => {
                  setFilterName('')
                  setFilterMuscleGroup('')
                  setFilterEnabled('all')
                }}
                style={{
                  padding: '8px 16px',
                  background: '#f0f0f0',
                  border: '1px solid rgba(0, 0, 0, 0.1)',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#4A4A4A'
                }}
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* Scrollable Exercise List */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          paddingRight: '8px',
          marginRight: '-8px'
        }}>
          {getFilteredExercises().length === 0 ? (
            <p style={{ textAlign: 'center', padding: '40px' }}>
              {exercises.length === 0 
                ? 'No exercises found. Create your first exercise above.'
                : 'No exercises match the current filters.'}
            </p>
          ) : (
            <div style={{ display: 'grid', gap: '16px' }}>
              {getFilteredExercises().map(exercise => (
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
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <h3 style={{ margin: 0, fontSize: '18px' }}>{exercise.name}</h3>
                    {!exercise.enabled && (
                      <span style={{
                        padding: '2px 8px',
                        background: '#ff6b6b',
                        color: 'white',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: '600',
                        textTransform: 'uppercase'
                      }}>
                        Disabled
                      </span>
                    )}
                  </div>
                  <p style={{ margin: '0', fontSize: '14px' }}>
                    Primary: <strong>{exercise.primary_muscle_group_ids && exercise.primary_muscle_group_ids.length > 0 
                      ? exercise.primary_muscle_group_ids.map(id => getMuscleGroupName(id)).join(', ')
                      : 'None'}</strong>
                    {exercise.secondary_muscle_group_ids && exercise.secondary_muscle_group_ids.length > 0 && (
                      <span style={{ marginLeft: '15px' }}>
                        Secondary: {exercise.secondary_muscle_group_ids.map(id => getMuscleGroupName(id)).join(', ')}
                      </span>
                    )}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <button
                    onClick={() => handleToggleEnabled(exercise)}
                    style={{ 
                      fontSize: '14px', 
                      padding: '8px 16px',
                      background: exercise.enabled 
                        ? 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)'
                        : 'linear-gradient(135deg, #51cf66 0%, #40c057 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: 600,
                      transition: 'all 0.2s ease'
                    }}
                    title={exercise.enabled ? 'Disable exercise' : 'Enable exercise'}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'scale(1.05)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scale(1)'
                    }}
                  >
                    {exercise.enabled ? 'Disable' : 'Enable'}
                  </button>
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
    </div>
  )
}

