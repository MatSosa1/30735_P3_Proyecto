<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/auth'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

async function onSubmit() {
  errorMessage.value = ''
  loading.value = true

  try {
    const { data } = await login(username.value, password.value)

    auth.setTempSession(data.temp_token, data.roles)

    router.push('/select-role')
  } catch {
    // Mensaje genérico a propósito: no revela si falló el usuario o la contraseña (Zero Trust)
    errorMessage.value = 'Usuario o contraseña incorrectos.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="flex min-h-dvh items-center justify-center bg-bg px-4">
    <form
      class="w-full max-w-sm rounded-2xl border border-border bg-surface p-8 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.08)]"
      novalidate
      @submit.prevent="onSubmit"
    >
      <div class="text-center">
        <h1 class="text-xl font-semibold text-ink">Master Gateway</h1>
        <p class="mt-1 text-sm text-ink-secondary">Ingresá tus credenciales para continuar.</p>
      </div>

      <div class="mt-6 flex flex-col gap-4">
        <div class="flex flex-col gap-1.5">
          <label for="username" class="text-sm font-medium text-ink">Usuario</label>
          <input
            id="username"
            v-model="username"
            type="text"
            autocomplete="username"
            required
            class="rounded-lg border border-border bg-bg px-3 py-2 text-sm text-ink outline-none focus-visible:ring-2 focus-visible:ring-accent"
          />
        </div>

        <div class="flex flex-col gap-1.5">
          <label for="password" class="text-sm font-medium text-ink">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
            class="rounded-lg border border-border bg-bg px-3 py-2 text-sm text-ink outline-none focus-visible:ring-2 focus-visible:ring-accent"
          />
        </div>

        <p
          v-if="errorMessage"
          class="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger"
          role="alert"
          aria-describedby="password"
        >
          {{ errorMessage }}
        </p>

        <button
          type="submit"
          :disabled="loading"
          class="mt-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-ink transition active:scale-[0.98] disabled:opacity-60"
        >
          {{ loading ? 'Ingresando…' : 'Ingresar' }}
        </button>
      </div>
    </form>
  </main>
</template>
