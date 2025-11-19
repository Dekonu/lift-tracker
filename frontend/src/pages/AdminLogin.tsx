import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function AdminLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, logout, user } = useAuth()
  const navigate = useNavigate()

  // Check if user becomes a superuser after login
  useEffect(() => {
    if (user && user.is_superuser) {
      setLoading(false)
      navigate('/admin')
    } else if (user && !user.is_superuser && !loading) {
      setError('Access denied. Admin privileges required.')
      logout()
      setLoading(false)
    }
  }, [user, navigate, logout, loading])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      // User data will be fetched by login, useEffect will handle navigation
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to log in')
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ maxWidth: '450px', marginTop: '80px' }}>
      <div className="card">
        <h1 style={{ marginBottom: '24px', textAlign: 'center' }}>Admin Login</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="error">{error}</div>}
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '10px' }} disabled={loading}>
            {loading ? 'Logging in...' : 'Login as Admin'}
          </button>
        </form>
      </div>
    </div>
  )
}

