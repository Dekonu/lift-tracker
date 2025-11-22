import axios, { AxiosError } from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
const token = localStorage.getItem('access_token')
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Response interceptor to handle authentication errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle 401 Unauthorized errors
    if (error.response?.status === 401) {
      // Clear authentication data
      localStorage.removeItem('access_token')
      delete api.defaults.headers.common['Authorization']
      
      // Only redirect if we're not already on the login page
      const currentPath = window.location.pathname
      if (currentPath !== '/login' && currentPath !== '/admin/login' && currentPath !== '/signup') {
        // Redirect to login page
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

export default api

