<script setup>
import { useToast } from '../composables/useToast'

const { toasts, dismiss } = useToast()
</script>

<template>
  <div class="fixed bottom-4 right-4 z-toast flex flex-col gap-2" aria-live="polite">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="flex items-center gap-3 rounded-lg border px-4 py-3 text-sm shadow-sm"
        :class="toast.type === 'error'
          ? 'border-danger/20 bg-danger/10 text-danger'
          : 'border-success/20 bg-success/10 text-success'"
        role="status"
      >
        <span>{{ toast.message }}</span>
        <button
          type="button"
          class="ml-auto text-ink-muted hover:text-ink"
          aria-label="Cerrar notificación"
          @click="dismiss(toast.id)"
        >
          ×
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 180ms cubic-bezier(0.16, 1, 0.3, 1), transform 180ms cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
