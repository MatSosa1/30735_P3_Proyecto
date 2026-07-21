import { apiClient } from './client'

export function getModules() {
  return apiClient.get('/modules/')
}

export function getModule(id) {
  return apiClient.get(`/modules/${id}`)
}

export function createModule(payload) {
  return apiClient.post('/modules/', payload)
}

export function updateModule(id, payload) {
  return apiClient.patch(`/modules/${id}`, payload)
}

export function deleteModule(id) {
  return apiClient.delete(`/modules/${id}`)
}

export function setModuleRoles(id, rolesId) {
  return apiClient.put(`/modules/${id}/roles`, { roles_id: rolesId })
}
