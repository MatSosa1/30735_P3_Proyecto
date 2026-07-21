import { defineStore } from 'pinia'

// Solo para mostrar el username en la UI (ej. saludo, header) — nunca se usa para autorizar nada,
// eso lo sigue validando exclusivamente el backend en cada request.
function usernameFromToken(token) {
  try {
    return JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))?.user ?? null
  } catch {
    return null
  }
}

// Todo en memoria a propósito (nada en localStorage/sessionStorage): un refresh de página
// cierra la sesión y obliga a loguearse de nuevo. Es la opción más simple y más segura para
// este MVP sin tener que agregar soporte de cookies httpOnly en el backend todavía.
export const useAuthStore = defineStore('auth', {
  state: () => ({
    tempToken: null,
    token: null,
    refreshToken: null,
    roles: [],
    currentRole: null,
    menuTree: [],
    username: null,
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    hasTempSession: (state) => Boolean(state.tempToken),
  },

  actions: {
    setTempSession(tempToken, roles) {
      this.tempToken = tempToken
      this.roles = roles
    },

    setSession(token, refreshToken, role) {
      this.token = token
      this.refreshToken = refreshToken
      this.currentRole = role
      this.tempToken = null
      this.username = usernameFromToken(token)
    },

    setMenuTree(tree) {
      this.menuTree = tree
    },

    clearSession() {
      this.tempToken = null
      this.token = null
      this.refreshToken = null
      this.roles = []
      this.currentRole = null
      this.menuTree = []
      this.username = null
    },
  },
})
