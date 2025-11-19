import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Home from './pages/Home'
import CreateWorkout from './pages/CreateWorkout'
import AdminLogin from './pages/AdminLogin'
import AdminDashboard from './pages/AdminDashboard'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="container">Loading...</div>
  }
  
  return user ? <>{children}</> : <Navigate to="/login" />
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="container">Loading...</div>
  }
  
  if (!user) {
    return <Navigate to="/admin/login" />
  }
  
  if (!user.is_superuser) {
    return <Navigate to="/home" />
  }
  
  return <>{children}</>
}

function AppRoutes() {
  const { user } = useAuth()
  
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/home" /> : <Login />} />
      <Route path="/signup" element={user ? <Navigate to="/home" /> : <Signup />} />
      <Route path="/admin/login" element={user?.is_superuser ? <Navigate to="/admin" /> : <AdminLogin />} />
      <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
      <Route path="/home" element={<PrivateRoute><Home /></PrivateRoute>} />
      <Route path="/workout/create" element={<PrivateRoute><CreateWorkout /></PrivateRoute>} />
      <Route path="/" element={<Navigate to="/home" />} />
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  )
}

export default App

