import { apiClient } from './client'

export function getUsers() {
  return apiClient.get('/users/')
}

export function getUser(id) {
  return apiClient.get(`/users/${id}`)
}

export function createUser(payload) {
  return apiClient.post('/users/', payload)
}

export function updateUser(id, payload) {
  return apiClient.patch(`/users/${id}`, payload)
}

export function deleteUser(id) {
  return apiClient.delete(`/users/${id}`)
}
