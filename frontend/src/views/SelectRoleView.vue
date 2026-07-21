<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { selectRole } from '../api/auth'
import { getMenuTree } from '../api/menus'
import { useAuthStore } from '../stores/auth'
import { registerDynamicRoutes } from '../router/dynamicRoutes'

const router = useRouter()
const auth = useAuthStore()

const errorMessage = ref('')
const loadingRoleId = ref(null)

async function choose(role) {
  errorMessage.value = ''
  loadingRoleId.value = role.id_role

  try {
    const { data } = await selectRole(auth.tempToken, role.id_role)

    auth.setSession(data.token, data.refresh_token, role)

    const { data: tree } = await getMenuTree()

    auth.setMenuTree(tree)
    registerDynamicRoutes(router, tree)

    router.push('/app')
  } catch {
    errorMessage.value = 'No se pudo iniciar sesión con ese rol. Volvé a intentar.'
  } finally {
    loadingRoleId.value = null
  }
}
</script>

<template>
  <main class="flex min-h-dvh items-center justify-center bg-bg px-4">
    <div class="w-full max-w-md">
      <h1 class="text-xl font-semibold text-ink">Elegí tu espacio de trabajo</h1>
      <p class="mt-1 text-sm text-ink-secondary">
        Seleccioná el rol con el que querés operar en esta sesión.
      </p>

      <p v-if="errorMessage" class="mt-4 rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger" role="alert">
        {{ errorMessage }}
      </p>

      <ul class="mt-6 flex flex-col gap-3">
        <li v-for="role in auth.roles" :key="role.id_role">
          <button
            type="button"
            :disabled="loadingRoleId !== null"
            class="flex w-full items-center justify-between rounded-xl border border-border bg-surface px-4 py-3 text-left text-sm font-medium text-ink transition hover:border-accent disabled:opacity-60"
            @click="choose(role)"
          >
            {{ role.name_role }}
            <span class="text-ink-muted">{{ loadingRoleId === role.id_role ? 'Ingresando…' : '→' }}</span>
          </button>
        </li>
      </ul>
    </div>
  </main>
</template>
