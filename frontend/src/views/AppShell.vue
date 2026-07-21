<script setup>
import { useRouter } from 'vue-router'
import { PhSignOut } from '@phosphor-icons/vue'
import { logout as logoutRequest } from '../api/auth'
import { useAuthStore } from '../stores/auth'
import Sidebar from '../components/Sidebar.vue'
import { useToast } from '../composables/useToast'

const auth = useAuthStore()
const router = useRouter()
const toast = useToast()

async function onLogout() {
  try {
    await logoutRequest()
  } catch {
    // Si falla la llamada igual cerramos la sesión localmente
  } finally {
    auth.clearSession()
    toast.success('Sesión cerrada.')
    router.push('/login')
  }
}
</script>

<template>
  <div class="flex min-h-dvh bg-bg">
    <Sidebar />

    <div class="flex min-w-0 flex-1 flex-col">
      <header class="flex items-center justify-between border-b border-border bg-surface px-6 py-3">
        <span class="rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
          {{ auth.currentRole?.name_role }}
        </span>

        <button
          type="button"
          class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-ink-secondary transition hover:bg-ink/5 hover:text-ink"
          @click="onLogout"
        >
          <PhSignOut class="size-4" aria-hidden="true" />
          Cerrar sesión
        </button>
      </header>

      <main class="mx-auto w-full max-w-[1280px] flex-1 p-6 md:p-8">
        <router-view />
      </main>
    </div>
  </div>
</template>
