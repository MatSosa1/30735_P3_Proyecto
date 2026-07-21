import { apiClient } from './client'

export function getMenuTree() {
  return apiClient.get('/menus/tree')
}
