<script setup>
defineProps({
  title: { type: String, default: '' },
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-ink">{{ title }}</h1>
    <p class="mt-1 text-sm text-ink-secondary">
      Este módulo todavía no tiene una pantalla propia en el frontend.
    </p>
  </div>
</template>
