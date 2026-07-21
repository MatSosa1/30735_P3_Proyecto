import { apiClient } from './client'

export function getRoles() {
  return apiClient.get('/roles/')
}

export function getRole(id) {
  return apiClient.get(`/roles/${id}`)
}

export function createRole(payload) {
  return apiClient.post('/roles/', payload)
}

export function updateRole(id, payload) {
  return apiClient.patch(`/roles/${id}`, payload)
}

export function deleteRole(id) {
  return apiClient.delete(`/roles/${id}`)
}

export function assignUserToRole(roleId, userId) {
  return apiClient.post(`/roles/${roleId}/users`, { user_id: userId })
}

export function unassignUserFromRole(roleId, userId) {
  return apiClient.delete(`/roles/${roleId}/users/${userId}`)
}

export function assignModuleToRole(roleId, moduleId) {
  return apiClient.post(`/roles/${roleId}/modules`, { module_id: moduleId })
}
