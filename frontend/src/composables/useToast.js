import { reactive } from 'vue'

const toasts = reactive([])
let nextId = 1

function push(message, type = 'success') {
  const id = nextId++

  toasts.push({ id, message, type })

  setTimeout(() => dismiss(id), 4000)
}

function dismiss(id) {
  const index = toasts.findIndex((toast) => toast.id === id)

  if (index !== -1) toasts.splice(index, 1)
}

export function useToast() {
  return {
    toasts,
    success: (message) => push(message, 'success'),
    error: (message) => push(message, 'error'),
    dismiss,
  }
}
