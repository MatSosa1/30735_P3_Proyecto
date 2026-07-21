<script setup>
import { computed, onMounted, ref } from 'vue'
import { PhPencilSimple, PhPlus, PhTrash } from '@phosphor-icons/vue'
import { createModule, deleteModule, getModules, updateModule } from '../../api/modules'
import DataTable from '../../components/DataTable.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import { useToast } from '../../composables/useToast'

const toast = useToast()

const columns = [
  { key: 'id_module', label: 'ID', mono: true },
  { key: 'name_module', label: 'Nombre' },
  { key: 'url_module', label: 'URL', mono: true },
  { key: 'estado', label: 'Estado' },
]

const modules = ref([])
const loading = ref(true)

const formDialog = ref(null)
const confirmDialog = ref(null)
const editingModule = ref(null)
const pendingDeleteId = ref(null)

const form = ref({ name: '', url: '', parent_id: '' })
const formError = ref('')
const submitting = ref(false)

// Combo de padre con indentación visual según profundidad, en vez de una lista plana de IDs
const parentOptions = computed(() => {
  const byParent = new Map()

  for (const module of modules.value) {
    if (editingModule.value && module.id_module === editingModule.value.id_module) continue

    const key = module.parent_id_module ?? 'root'
    if (!byParent.has(key)) byParent.set(key, [])
    byParent.get(key).push(module)
  }

  const options = []

  function walk(parentKey, depth) {
    for (const module of byParent.get(parentKey) ?? []) {
      options.push({ id: module.id_module, label: `${'—'.repeat(depth)} ${module.name_module}`.trim() })
      walk(module.id_module, depth + 1)
    }
  }

  walk('root', 0)

  return options
})

async function load() {
  loading.value = true
  try {
    const { data } = await getModules()
    modules.value = data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingModule.value = null
  form.value = { name: '', url: '', parent_id: '' }
  formError.value = ''
  formDialog.value?.showModal()
}

function openEdit(module) {
  editingModule.value = module
  form.value = {
    name: module.name_module,
    url: module.url_module ?? '',
    parent_id: module.parent_id_module ?? '',
  }
  formError.value = ''
  formDialog.value?.showModal()
}

async function onSubmit() {
  formError.value = ''
  submitting.value = true

  const payload = {
    name: form.value.name,
    url: form.value.url,
    parent_id: form.value.parent_id === '' ? null : Number(form.value.parent_id),
  }

  try {
    if (editingModule.value) {
      await updateModule(editingModule.value.id_module, payload)
      toast.success('Módulo actualizado.')
    } else {
      await createModule(payload)
      toast.success('Módulo creado.')
    }

    formDialog.value?.close()
    await load()
  } catch (error) {
    formError.value = error.response?.data?.detail ?? 'No se pudo guardar el módulo.'
  } finally {
    submitting.value = false
  }
}

function askDelete(module) {
  pendingDeleteId.value = module.id_module
  confirmDialog.value?.open()
}

async function onConfirmDelete() {
  try {
    await deleteModule(pendingDeleteId.value)
    toast.success('Módulo desactivado.')
    await load()
  } catch {
    toast.error('No se pudo eliminar el módulo.')
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-ink">Módulos</h1>
      <button
        type="button"
        class="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-ink transition active:scale-[0.98]"
        @click="openCreate"
      >
        <PhPlus class="size-4" aria-hidden="true" />
        Nuevo módulo
      </button>
    </div>

    <div class="mt-6">
      <DataTable :columns="columns" :rows="modules" row-key="id_module" :loading="loading" empty-message="Todavía no hay módulos registrados.">
        <template #cell-url_module="{ row }">
          {{ row.url_module || '—' }}
        </template>

        <template #cell-estado="{ row }">
          <StatusBadge :estado="row.estado" />
        </template>

        <template #actions="{ row }">
          <button type="button" class="rounded-lg p-2 text-ink-secondary transition hover:bg-ink/5 hover:text-ink" aria-label="Editar módulo" @click="openEdit(row)">
            <PhPencilSimple class="size-4" aria-hidden="true" />
          </button>
          <button type="button" class="rounded-lg p-2 text-ink-secondary transition hover:bg-danger/10 hover:text-danger" aria-label="Eliminar módulo" @click="askDelete(row)">
            <PhTrash class="size-4" aria-hidden="true" />
          </button>
        </template>
      </DataTable>
    </div>

    <dialog ref="formDialog" class="z-modal w-full max-w-sm rounded-xl border border-border bg-surface p-0 text-ink backdrop:bg-ink/40">
      <form class="p-6" novalidate @submit.prevent="onSubmit">
        <h2 class="text-base font-semibold">{{ editingModule ? 'Editar módulo' : 'Nuevo módulo' }}</h2>

        <div class="mt-4 flex flex-col gap-4">
          <div class="flex flex-col gap-1.5">
            <label for="module-name" class="text-sm font-medium">Nombre</label>
            <input id="module-name" v-model="form.name" required class="rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-accent" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label for="module-url" class="text-sm font-medium">URL <span class="font-normal text-ink-muted">(solo nodos hoja)</span></label>
            <input id="module-url" v-model="form.url" placeholder="/ejemplo" class="rounded-lg border border-border bg-bg px-3 py-2 text-sm font-mono outline-none focus-visible:ring-2 focus-visible:ring-accent" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label for="module-parent" class="text-sm font-medium">Módulo padre</label>
            <select id="module-parent" v-model="form.parent_id" class="rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-accent">
              <option value="">— Ninguno (nodo raíz) —</option>
              <option v-for="option in parentOptions" :key="option.id" :value="option.id">{{ option.label }}</option>
            </select>
          </div>
        </div>

        <p v-if="formError" class="mt-4 rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger" role="alert">{{ formError }}</p>

        <div class="mt-6 flex justify-end gap-3">
          <button type="button" class="rounded-lg px-4 py-2 text-sm font-medium text-ink-secondary hover:bg-ink/5" @click="formDialog?.close()">Cancelar</button>
          <button type="submit" :disabled="submitting" class="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-ink transition active:scale-[0.98] disabled:opacity-60">Guardar</button>
        </div>
      </form>
    </dialog>

    <ConfirmDialog
      ref="confirmDialog"
      title="Eliminar módulo"
      message="El módulo (y todo lo que cuelgue de él en el árbol de menú) dejará de renderizarse en la navegación."
      confirm-label="Eliminar"
      @confirm="onConfirmDelete"
    />
  </div>
</template>
