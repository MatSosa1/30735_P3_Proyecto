<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  message: { type: String, required: true },
  confirmLabel: { type: String, default: 'Confirmar' },
})

const emit = defineEmits(['confirm'])

const dialogEl = ref(null)

function open() {
  dialogEl.value?.showModal()
}

function confirm() {
  emit('confirm')
  dialogEl.value?.close()
}

defineExpose({ open })
</script>

<template>
  <dialog
    ref="dialogEl"
    class="z-modal w-full max-w-sm rounded-xl border border-border bg-surface p-0 text-ink backdrop:bg-ink/40"
  >
    <div class="p-6">
      <h2 class="text-base font-semibold">{{ props.title }}</h2>
      <p class="mt-2 text-sm text-ink-secondary">{{ props.message }}</p>

      <div class="mt-6 flex justify-end gap-3">
        <button
          type="button"
          class="rounded-lg px-4 py-2 text-sm font-medium text-ink-secondary hover:bg-ink/5"
          @click="dialogEl?.close()"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="rounded-lg bg-danger px-4 py-2 text-sm font-medium text-white transition active:scale-[0.98]"
          @click="confirm"
        >
          {{ props.confirmLabel }}
        </button>
      </div>
    </div>
  </dialog>
</template>
