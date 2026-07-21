import { apiClient } from './client'

export function login(username, password) {
  return apiClient.post('/auth/login', { username, password })
}

export function selectRole(tempToken, roleId) {
  return apiClient.post('/auth/select-role', { temp_token: tempToken, role_id: roleId })
}

export function logout() {
  return apiClient.post('/auth/logout')
}
