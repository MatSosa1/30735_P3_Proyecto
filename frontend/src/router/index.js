import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import SelectRoleView from '../views/SelectRoleView.vue'
import AppShell from '../views/AppShell.vue'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView },
    { path: '/select-role', name: 'select-role', component: SelectRoleView },
    {
      path: '/app',
      name: 'app',
      component: AppShell,
      children: [{ path: '', name: 'home', component: HomeView }],
      // Los hijos de esta ruta ("app") se completan en runtime (ver dynamicRoutes.js) a partir
      // del árbol de menú devuelto por el backend tras seleccionar rol — nunca están hardcodeados.
    },
    { path: '/', redirect: '/login' },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.name === 'select-role') {
    if (!auth.hasTempSession) return { name: 'login' }
    return true
  }

  if (to.path.startsWith('/app')) {
    if (!auth.isAuthenticated) return { name: 'login' }
    return true
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'home' }
  }

  return true
})

export default router
