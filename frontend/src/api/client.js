import axios from 'axios'
import { useAuthStore } from '../stores/auth'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

apiClient.interceptors.request.use((config) => {
  const auth = useAuthStore()

  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }

  return config
})

let refreshInFlight = null

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const auth = useAuthStore()
    const originalRequest = error.config

    const isAuthEndpoint = originalRequest?.url?.includes('/auth/')

    if (error.response?.status !== 401 || isAuthEndpoint || originalRequest._retried) {
      return Promise.reject(error)
    }

    if (!auth.refreshToken) {
      auth.clearSession()
      return Promise.reject(error)
    }

    originalRequest._retried = true

    try {
      // Varias requests pueden fallar con 401 al mismo tiempo: se comparte una única
      // llamada de refresh en curso en vez de disparar una por cada una.
      refreshInFlight ??= apiClient.post('/auth/refresh-token', {
        refresh_token: auth.refreshToken,
      })

      const { data } = await refreshInFlight
      refreshInFlight = null

      auth.setSession(data.token, data.refresh_token, auth.currentRole)

      originalRequest.headers.Authorization = `Bearer ${data.token}`

      return apiClient(originalRequest)
    } catch (refreshError) {
      refreshInFlight = null
      auth.clearSession()

      return Promise.reject(refreshError)
    }
  }
)
