<script setup>
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="rounded-xl border border-border bg-surface p-8">
    <h1 class="text-2xl font-bold text-ink">¡Bienvenido, {{ auth.username }}!</h1>
    <p class="mt-2 text-base text-ink-secondary">
      Estás operando como <strong class="font-semibold text-ink">{{ auth.currentRole?.name_role }}</strong>.
    </p>
    <p class="mt-4 text-sm text-ink-muted">
      Usá el menú de navegación para acceder a los módulos disponibles para este rol.
    </p>
  </div>
</template>
