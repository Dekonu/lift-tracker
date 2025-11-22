import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface Equipment {
  id: number
  name: string
  description: string | null
  enabled: boolean
}

export default function EquipmentManagement() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [equipment, setEquipment] = useState<Equipment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingEquipment, setEditingEquipment] = useState<Equipment | null>(null)
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<{created: number, updated: number, skipped: number, errors: string[]} | null>(null)
  const [wgerSyncMode, setWgerSyncMode] = useState<'partial' | 'full'>('partial')
  const [wgerSyncing, setWgerSyncing] = useState(false)
  const [wgerSyncResult, setWgerSyncResult] = useState<{created: number, updated: number, skipped: number, errors: string[]} | null>(null)
  
  // Filter state
  const [filterName, setFilterName] = useState('')
  const [filterEnabled, setFilterEnabled] = useState<'all' | 'enabled' | 'disabled'>('all')
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    enabled: true
  })

  useEffect(() => {
    // Check if user is superuser
    if (!user?.is_superuser) {
      navigate('/home')
      return
    }
    fetchEquipment()
  }, [user, navigate])

  async function fetchEquipment() {
    try {
      setLoading(true)
      const response = await api.get('/v1/equipment?items_per_page=1000')
      const equipmentData = response.data.data || []
      setEquipment(equipmentData)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch equipment')
    } finally {
      setLoading(false)
    }
  }

  function getFilteredEquipment(): Equipment[] {
    return equipment.filter(eq => {
      // Filter by name
      if (filterName && !eq.name.toLowerCase().includes(filterName.toLowerCase())) {
        return false
      }
      
      // Filter by enabled status
      if (filterEnabled === 'enabled' && !eq.enabled) {
        return false
      }
      if (filterEnabled === 'disabled' && eq.enabled) {
        return false
      }
      
      return true
    })
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (editingEquipment) {
        await api.patch(`/v1/equipment/${editingEquipment.id}`, {
          name: formData.name,
          description: formData.description || null,
          enabled: formData.enabled
        })
      } else {
        await api.post('/v1/equipment', {
          name: formData.name,
          description: formData.description || null,
          enabled: formData.enabled
        })
      }
      setFormData({
        name: '',
        description: '',
        enabled: true
      })
      setShowAddForm(false)
      setEditingEquipment(null)
      await fetchEquipment()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save equipment')
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm('Are you sure you want to delete this equipment?')) {
      return
    }
    try {
      await api.delete(`/v1/equipment/${id}`)
      await fetchEquipment()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete equipment')
    }
  }

  function handleEdit(eq: Equipment) {
    setEditingEquipment(eq)
    setFormData({
      name: eq.name,
      description: eq.description || '',
      enabled: eq.enabled
    })
    setShowAddForm(true)
  }

  async function handleToggleEnabled(eq: Equipment) {
    try {
      await api.patch(`/v1/equipment/${eq.id}`, {
        enabled: !eq.enabled
      })
      await fetchEquipment()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to toggle equipment status')
    }
  }

  async function handleExport() {
    try {
      const response = await api.get('/v1/equipment/export', {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'equipment_export.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to export equipment')
    }
  }

  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    
    try {
      setImporting(true)
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post('/v1/equipment/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      setImportResult(response.data)
      await fetchEquipment()
      // Reset file input
      e.target.value = ''
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import equipment')
    } finally {
      setImporting(false)
    }
  }

  async function handleWgerSync() {
    try {
      setWgerSyncing(true)
      const response = await api.post(`/v1/equipment/sync-wger?full_sync=${wgerSyncMode === 'full'}`)
      setWgerSyncResult(response.data)
      await fetchEquipment()
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
        <h1>Equipment Management</h1>
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
              setEditingEquipment(null)
              setFormData({
                name: '',
                description: '',
                enabled: true
              })
            }}
          >
            {showAddForm ? 'Cancel' : 'Add Equipment'}
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
              title="Sync equipment from Wger API"
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

      {showAddForm && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <h2>{editingEquipment ? 'Edit Equipment' : 'Add New Equipment'}</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Equipment Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                maxLength={50}
              />
            </div>

            <div className="form-group">
              <label>Description (optional)</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                maxLength={200}
                rows={3}
              />
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
                {editingEquipment ? 'Update Equipment' : 'Create Equipment'}
              </button>
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={() => {
                  setShowAddForm(false)
                  setEditingEquipment(null)
                  setFormData({
                    name: '',
                    description: '',
                    enabled: true
                  })
                }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="card" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 200px)', minHeight: '600px' }}>
        <div style={{ flexShrink: 0 }}>
          <h2 style={{ marginBottom: '20px' }}>Equipment ({equipment.length}) {getFilteredEquipment().length !== equipment.length && `(Filtered: ${getFilteredEquipment().length})`}</h2>
        
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
                placeholder="Search equipment name..."
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
                <option value="all">All Equipment</option>
                <option value="enabled">Enabled Only</option>
                <option value="disabled">Disabled Only</option>
              </select>
            </div>
            
            {(filterName || filterEnabled !== 'all') && (
              <button
                type="button"
                onClick={() => {
                  setFilterName('')
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

        {/* Scrollable Equipment List */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          paddingRight: '8px',
          marginRight: '-8px'
        }}>
          {getFilteredEquipment().length === 0 ? (
            <p style={{ textAlign: 'center', padding: '40px' }}>
              {equipment.length === 0 
                ? 'No equipment found. Create your first equipment above.'
                : 'No equipment matches the current filters.'}
            </p>
          ) : (
            <div style={{ display: 'grid', gap: '16px' }}>
              {getFilteredEquipment().map(eq => (
              <div
                key={eq.id}
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
                    <h3 style={{ margin: 0, fontSize: '18px' }}>{eq.name}</h3>
                    {!eq.enabled && (
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
                  {eq.description && (
                    <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                      {eq.description}
                    </p>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <button
                    onClick={() => handleToggleEnabled(eq)}
                    style={{ 
                      fontSize: '14px', 
                      padding: '8px 16px',
                      background: eq.enabled 
                        ? 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)'
                        : 'linear-gradient(135deg, #51cf66 0%, #40c057 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: 600,
                      transition: 'all 0.2s ease'
                    }}
                    title={eq.enabled ? 'Disable equipment' : 'Enable equipment'}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'scale(1.05)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scale(1)'
                    }}
                  >
                    {eq.enabled ? 'Disable' : 'Enable'}
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={() => handleEdit(eq)}
                    style={{ fontSize: '14px', padding: '8px 16px' }}
                  >
                    Edit
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDelete(eq.id)}
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

