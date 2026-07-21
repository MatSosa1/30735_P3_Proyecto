<script setup>
import { ref } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { PhList, PhSignOut, PhTreeStructure, PhX } from '@phosphor-icons/vue'
import { logout as logoutRequest } from '../api/auth'
import { useAuthStore } from '../stores/auth'
import { useToast } from '../composables/useToast'
import SidebarNode from '../components/SidebarNode.vue'

const auth = useAuthStore()
const router = useRouter()
const toast = useToast()

const sidebarOpen = ref(false)

async function onLogout() {
  try {
    await logoutRequest()
  } catch {
    // Si falla la llamada igual cerramos la sesión localmente
  } finally {
    auth.clearSession()
    toast.success('Sesión cerrada.')
    router.push({ name: 'login' })
  }
}

// Delegación simple: cualquier click en un link del drawer móvil lo cierra, sin acoplar
// SidebarNode a un evento "navigate" que solo tiene sentido en este layout.
function onMobileNavClick(event) {
  if (event.target.closest('a')) sidebarOpen.value = false
}
</script>

<template>
  <div class="flex h-dvh bg-bg">
    <!-- Sidebar fija (desktop) -->
    <aside class="hidden w-64 shrink-0 flex-col border-r border-border bg-surface lg:flex">
      <div class="flex h-16 shrink-0 items-center gap-2 border-b border-border px-4 text-sm font-semibold text-ink">
        <PhTreeStructure class="size-5 text-accent" aria-hidden="true" />
        Master Gateway
      </div>
      <nav class="flex-1 overflow-y-auto p-4" aria-label="Menú principal">
        <ul class="flex flex-col gap-0.5">
          <li>
            <RouterLink
              to="/app"
              class="flex items-center rounded-lg px-3 py-2 text-sm text-ink-secondary transition hover:bg-ink/5 hover:text-ink"
              active-class="bg-accent/10 text-accent font-medium"
              exact-active-class="bg-accent/10 text-accent font-medium"
            >
              Inicio
            </RouterLink>
          </li>
          <SidebarNode v-for="node in auth.menuTree" :key="node.id_module" :node="node" />
        </ul>
      </nav>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col">
      <header class="z-sticky sticky top-0 flex items-center justify-between border-b border-border bg-surface px-4 py-3 sm:px-6">
        <button
          type="button"
          class="rounded-lg p-2 text-ink-secondary transition hover:bg-ink/5 hover:text-ink lg:hidden"
          aria-label="Abrir menú"
          @click="sidebarOpen = true"
        >
          <PhList class="size-5" aria-hidden="true" />
        </button>

        <div class="flex flex-1 items-center justify-end gap-3">
          <div class="hidden text-right sm:block">
            <p class="text-sm font-medium text-ink">{{ auth.username }}</p>
          </div>
          <span class="rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
            {{ auth.currentRole?.name_role }}
          </span>

          <button
            type="button"
            class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-ink-secondary transition hover:bg-ink/5 hover:text-ink"
            @click="onLogout"
          >
            <PhSignOut class="size-4" aria-hidden="true" />
            <span class="hidden sm:inline">Cerrar sesión</span>
          </button>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto">
        <div class="mx-auto w-full max-w-[1280px] p-6 md:p-8">
          <RouterView />
        </div>
      </main>
    </div>

    <!-- Drawer móvil -->
    <div v-if="sidebarOpen" class="lg:hidden">
      <div class="z-modal-backdrop fixed inset-0 bg-ink/40" @click="sidebarOpen = false" />
      <div class="z-modal fixed inset-y-0 left-0 flex w-64 flex-col bg-surface" role="dialog" aria-modal="true" aria-label="Menú principal">
        <div class="flex h-16 shrink-0 items-center justify-between border-b border-border px-4">
          <div class="flex items-center gap-2 text-sm font-semibold text-ink">
            <PhTreeStructure class="size-5 text-accent" aria-hidden="true" />
            Master Gateway
          </div>
          <button type="button" class="rounded-lg p-2 text-ink-secondary hover:bg-ink/5 hover:text-ink" aria-label="Cerrar menú" @click="sidebarOpen = false">
            <PhX class="size-5" aria-hidden="true" />
          </button>
        </div>
        <nav class="flex-1 overflow-y-auto p-4" aria-label="Menú principal (móvil)" @click="onMobileNavClick">
          <ul class="flex flex-col gap-0.5">
            <li>
              <RouterLink
                to="/app"
                class="flex items-center rounded-lg px-3 py-2 text-sm text-ink-secondary transition hover:bg-ink/5 hover:text-ink"
                active-class="bg-accent/10 text-accent font-medium"
                exact-active-class="bg-accent/10 text-accent font-medium"
              >
                Inicio
              </RouterLink>
            </li>
            <SidebarNode v-for="node in auth.menuTree" :key="node.id_module" :node="node" />
          </ul>
        </nav>
      </div>
    </div>
  </div>
</template>
