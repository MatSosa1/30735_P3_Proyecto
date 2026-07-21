<script setup>
defineProps({
  estado: { type: String, required: true },
})
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium"
    :class="estado === 'ACTIVO'
      ? 'bg-success/10 text-success'
      : 'bg-ink-muted/10 text-ink-secondary'"
  >
    <span
      class="size-1.5 rounded-full"
      :class="estado === 'ACTIVO' ? 'bg-success' : 'bg-ink-muted'"
      aria-hidden="true"
    />
    {{ estado }}
  </span>
</template>
