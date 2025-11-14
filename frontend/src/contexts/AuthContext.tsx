import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import api from '../services/api'

interface User {
  id: number
  name: string
  email: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // Fetch current user
      api.get('/v1/user/me/')
        .then(response => {
          setUser(response.data)
        })
        .catch(() => {
          localStorage.removeItem('access_token')
          delete api.defaults.headers.common['Authorization']
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    // OAuth2PasswordRequestForm expects URL-encoded form data
    const params = new URLSearchParams()
    params.append('username', email) // OAuth2PasswordRequestForm uses 'username' field for email
    params.append('password', password)
    
    const response = await api.post('/v1/login', params.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    
    const { access_token } = response.data
    localStorage.setItem('access_token', access_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    
    // Fetch user data
    const userResponse = await api.get('/v1/user/me/')
    setUser(userResponse.data)
  }

  const signup = async (name: string, email: string, password: string) => {
    await api.post('/v1/user', { name, email, password })
    // After signup, automatically log in
    await login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

