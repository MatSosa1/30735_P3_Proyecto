<script setup>
import { onMounted, ref } from 'vue'
import { PhPencilSimple, PhPlus, PhTrash, PhUserCircle } from '@phosphor-icons/vue'
import { createRole, deleteRole, getRoles, updateRole, assignUserToRole } from '../../api/roles'
import { getUsers } from '../../api/users'
import DataTable from '../../components/DataTable.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import { useToast } from '../../composables/useToast'

const toast = useToast()

const columns = [
  { key: 'id_role', label: 'ID', mono: true },
  { key: 'name_role', label: 'Nombre' },
  { key: 'estado', label: 'Estado' },
]

const roles = ref([])
const users = ref([])
const loading = ref(true)

const formDialog = ref(null)
const assignDialog = ref(null)
const confirmDialog = ref(null)
const editingRole = ref(null)
const assigningRole = ref(null)
const pendingDeleteId = ref(null)

const form = ref({ name: '' })
const formError = ref('')
const submitting = ref(false)

const selectedUserId = ref('')
const assignError = ref('')

async function load() {
  loading.value = true
  try {
    const [rolesResponse, usersResponse] = await Promise.all([getRoles(), getUsers()])
    roles.value = rolesResponse.data
    users.value = usersResponse.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingRole.value = null
  form.value = { name: '' }
  formError.value = ''
  formDialog.value?.showModal()
}

function openEdit(role) {
  editingRole.value = role
  form.value = { name: role.name_role }
  formError.value = ''
  formDialog.value?.showModal()
}

async function onSubmit() {
  formError.value = ''
  submitting.value = true

  try {
    if (editingRole.value) {
      await updateRole(editingRole.value.id_role, form.value)
      toast.success('Rol actualizado.')
    } else {
      await createRole(form.value)
      toast.success('Rol creado.')
    }

    formDialog.value?.close()
    await load()
  } catch (error) {
    formError.value = error.response?.data?.detail ?? 'No se pudo guardar el rol.'
  } finally {
    submitting.value = false
  }
}

function askDelete(role) {
  pendingDeleteId.value = role.id_role
  confirmDialog.value?.open()
}

async function onConfirmDelete() {
  try {
    await deleteRole(pendingDeleteId.value)
    toast.success('Rol desactivado.')
    await load()
  } catch (error) {
    toast.error(
      error.response?.status === 409
        ? 'No se puede eliminar: el rol tiene usuarios activos asignados.'
        : 'No se pudo eliminar el rol.'
    )
  }
}

function openAssign(role) {
  assigningRole.value = role
  selectedUserId.value = ''
  assignError.value = ''
  assignDialog.value?.showModal()
}

async function onAssign() {
  assignError.value = ''

  try {
    await assignUserToRole(assigningRole.value.id_role, Number(selectedUserId.value))
    toast.success('Usuario asignado al rol.')
    assignDialog.value?.close()
  } catch {
    assignError.value = 'No se pudo asignar el usuario.'
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-ink">Roles</h1>
        <p class="mt-1 text-sm text-ink-secondary">
          Definí los roles del sistema y qué usuarios los tienen asignados.
        </p>
      </div>
      <button
        type="button"
        class="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-ink transition active:scale-[0.98]"
        @click="openCreate"
      >
        <PhPlus class="size-4" aria-hidden="true" />
        Nuevo rol
      </button>
    </div>

    <div class="mt-6">
      <DataTable :columns="columns" :rows="roles" row-key="id_role" :loading="loading" empty-message="Todavía no hay roles registrados.">
        <template #cell-estado="{ row }">
          <StatusBadge :estado="row.estado" />
        </template>

        <template #actions="{ row }">
          <button type="button" class="rounded-lg p-2 text-ink-secondary transition hover:bg-ink/5 hover:text-ink" aria-label="Asignar usuario" @click="openAssign(row)">
            <PhUserCircle class="size-4" aria-hidden="true" />
          </button>
          <button type="button" class="rounded-lg p-2 text-ink-secondary transition hover:bg-ink/5 hover:text-ink" aria-label="Editar rol" @click="openEdit(row)">
            <PhPencilSimple class="size-4" aria-hidden="true" />
          </button>
          <button type="button" class="rounded-lg p-2 text-ink-secondary transition hover:bg-danger/10 hover:text-danger" aria-label="Eliminar rol" @click="askDelete(row)">
            <PhTrash class="size-4" aria-hidden="true" />
          </button>
        </template>
      </DataTable>
    </div>

    <dialog ref="formDialog" class="z-modal w-full max-w-sm rounded-xl border border-border bg-surface p-0 text-ink backdrop:bg-ink/40">
      <form class="p-6" novalidate @submit.prevent="onSubmit">
        <h2 class="text-base font-semibold">{{ editingRole ? 'Editar rol' : 'Nuevo rol' }}</h2>

        <div class="mt-4 flex flex-col gap-1.5">
          <label for="role-name" class="text-sm font-medium">Nombre</label>
          <input id="role-name" v-model="form.name" required class="rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-accent" />
        </div>

        <p v-if="formError" class="mt-4 rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger" role="alert">{{ formError }}</p>

        <div class="mt-6 flex justify-end gap-3">
          <button type="button" class="rounded-lg px-4 py-2 text-sm font-medium text-ink-secondary hover:bg-ink/5" @click="formDialog?.close()">Cancelar</button>
          <button type="submit" :disabled="submitting" class="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-ink transition active:scale-[0.98] disabled:opacity-60">Guardar</button>
        </div>
      </form>
    </dialog>

    <dialog ref="assignDialog" class="z-modal w-full max-w-sm rounded-xl border border-border bg-surface p-0 text-ink backdrop:bg-ink/40">
      <form class="p-6" novalidate @submit.prevent="onAssign">
        <h2 class="text-base font-semibold">Asignar usuario a "{{ assigningRole?.name_role }}"</h2>

        <div class="mt-4 flex flex-col gap-1.5">
          <label for="assign-user" class="text-sm font-medium">Usuario</label>
          <select id="assign-user" v-model="selectedUserId" required class="rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-accent">
            <option value="" disabled>Seleccioná un usuario</option>
            <option v-for="user in users" :key="user.id_user" :value="user.id_user">
              {{ user.name_user }} {{ user.surname_user }} ({{ user.username_user }})
            </option>
          </select>
        </div>

        <p v-if="assignError" class="mt-4 rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger" role="alert">{{ assignError }}</p>

        <div class="mt-6 flex justify-end gap-3">
          <button type="button" class="rounded-lg px-4 py-2 text-sm font-medium text-ink-secondary hover:bg-ink/5" @click="assignDialog?.close()">Cancelar</button>
          <button type="submit" class="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-ink transition active:scale-[0.98]">Asignar</button>
        </div>
      </form>
    </dialog>

    <ConfirmDialog
      ref="confirmDialog"
      title="Eliminar rol"
      message="El rol quedará inactivo. Si tiene usuarios activos asignados, la eliminación será rechazada."
      confirm-label="Eliminar"
      @confirm="onConfirmDelete"
    />
  </div>
</template>
