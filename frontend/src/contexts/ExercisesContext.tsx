import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import api from '../services/api'
import { useAuth } from './AuthContext'

interface Exercise {
  id: number
  name: string
  primary_muscle_group_ids: number[]
  secondary_muscle_group_ids: number[]
  enabled: boolean
}

interface ExercisesContextType {
  exercises: Exercise[]
  loading: boolean
  error: string | null
  refreshExercises: () => Promise<void>
}

const ExercisesContext = createContext<ExercisesContextType | undefined>(undefined)

export function ExercisesProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchExercises = async () => {
    try {
      setLoading(true)
      setError(null)
      // Fetch all exercises (up to 1000) - since total is under 1000, fetch all at once
      // Only fetch enabled exercises for non-admin users (backend handles this)
      const response = await api.get('/v1/exercises?page=1&items_per_page=1000')
      const exercisesData = response.data.data || []
      const totalCount = response.data.total_count || 0
      
      // If no exercises found, provide helpful message
      if (exercisesData.length === 0 && totalCount === 0) {
        setError('No exercises found. Please sync exercises from Wger API in the admin dashboard.')
      } else if (exercisesData.length === 0 && totalCount > 0) {
        // All exercises are disabled
        setError('No enabled exercises available. Please enable exercises in the admin dashboard.')
      } else {
        // Clear error if we have exercises
        setError(null)
      }
      
      setExercises(exercisesData)
      
      // Cache in localStorage
      localStorage.setItem('exercises_cache', JSON.stringify({
        data: exercisesData,
        timestamp: Date.now()
      }))
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch exercises')
      // Try to load from cache on error
      const cached = localStorage.getItem('exercises_cache')
      if (cached) {
        try {
          const cachedData = JSON.parse(cached)
          // Use cache if less than 1 hour old
          if (Date.now() - cachedData.timestamp < 3600000) {
            setExercises(cachedData.data)
            setError(null) // Clear error if we have cached data
          }
        } catch {
          // Ignore cache parse errors
        }
      }
    } finally {
      setLoading(false)
    }
  }

  const refreshExercises = async () => {
    await fetchExercises()
  }

  useEffect(() => {
    // Only load exercises when user is authenticated
    if (!user) {
      setExercises([])
      setLoading(false)
      setError(null)
      return
    }

    // Try to load from cache first for instant display
    const cached = localStorage.getItem('exercises_cache')
    if (cached) {
      try {
        const cachedData = JSON.parse(cached)
        // Use cache if less than 1 hour old
        if (Date.now() - cachedData.timestamp < 3600000) {
          setExercises(cachedData.data)
          setLoading(false)
        }
      } catch {
        // Ignore cache parse errors
      }
    }
    
    // Always fetch fresh data in background when user logs in
    fetchExercises()
  }, [user])

  return (
    <ExercisesContext.Provider value={{ exercises, loading, error, refreshExercises }}>
      {children}
    </ExercisesContext.Provider>
  )
}

export function useExercises() {
  const context = useContext(ExercisesContext)
  if (context === undefined) {
    throw new Error('useExercises must be used within an ExercisesProvider')
  }
  return context
}

