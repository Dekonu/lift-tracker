import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function AdminDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is superuser
    if (!user?.is_superuser) {
      navigate('/home')
    }
  }, [user, navigate])

  if (!user?.is_superuser) {
    return <div className="container">Loading...</div>
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', flexWrap: 'wrap', gap: '16px' }}>
        <h1>Admin Dashboard</h1>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => navigate('/home')}>
            Back to Home
          </button>
          <button className="btn btn-secondary" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginTop: '40px', alignItems: 'stretch' }}>
        <div 
          className="card" 
          style={{ 
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            padding: '32px',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            height: '100%'
          }}
          onClick={() => navigate('/admin/exercises')}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)'
            e.currentTarget.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)'
          }}
        >
          <h2 style={{ marginBottom: '16px', color: '#4A4A4A' }}>💪 Exercise Management</h2>
          <p style={{ color: '#666', marginBottom: '20px', flex: 1 }}>
            Manage exercises, muscle groups, import/export CSV, and sync with Wger API
          </p>
          <button className="btn btn-primary" style={{ width: '100%', marginTop: 'auto' }}>
            Manage Exercises
          </button>
        </div>

        <div 
          className="card" 
          style={{ 
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            padding: '32px',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            height: '100%'
          }}
          onClick={() => navigate('/admin/equipment')}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)'
            e.currentTarget.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)'
          }}
        >
          <h2 style={{ marginBottom: '16px', color: '#4A4A4A' }}>🏋️ Equipment Management</h2>
          <p style={{ color: '#666', marginBottom: '20px', flex: 1 }}>
            Manage equipment, import/export CSV, and sync with Wger API
          </p>
          <button className="btn btn-primary" style={{ width: '100%', marginTop: 'auto' }}>
            Manage Equipment
          </button>
        </div>
      </div>
    </div>
  )
}
