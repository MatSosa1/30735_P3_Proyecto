<script setup>
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-ink">Bienvenido</h1>
    <p class="mt-1 text-sm text-ink-secondary">
      Estás operando como <strong class="text-ink">{{ auth.currentRole?.name_role }}</strong>.
      Usá el menú de la izquierda para navegar a los módulos disponibles para este rol.
    </p>
  </div>
</template>
