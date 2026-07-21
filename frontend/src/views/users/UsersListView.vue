<script setup>
import { computed, onMounted, ref } from 'vue'
import { PhPencilSimple, PhPlus, PhTrash } from '@phosphor-icons/vue'
import { createUser, deleteUser, getUsers, updateUser } from '../../api/users'
import DataTable from '../../components/DataTable.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'
import { useToast } from '../../composables/useToast'

const toast = useToast()

const columns = [
  { key: 'id_user', label: 'ID', mono: true },
  { key: 'name_user', label: 'Nombre' },
  { key: 'surname_user', label: 'Apellido' },
  { key: 'username_user', label: 'Usuario' },
  { key: 'estado', label: 'Estado' },
]

const users = ref([])
const loading = ref(true)

const formDialog = ref(null)
const confirmDialog = ref(null)
const editingUser = ref(null)
const pendingDeleteId = ref(null)

const form = ref({ name: '', surname: '', username: '', password: '' })
const formError = ref('')
const submitting = ref(false)

const passwordChecks = computed(() => ({
  length: form.value.password.length >= 8,
  upper: /[A-Z]/.test(form.value.password),
  lower: /[a-z]/.test(form.value.password),
  digit: /\d/.test(form.value.password),
}))

async function load() {
  loading.value = true
  try {
    const { data } = await getUsers()
    users.value = data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingUser.value = null
  form.value = { name: '', surname: '', username: '', password: '' }
  formError.value = ''
  formDialog.value?.showModal()
}

function openEdit(user) {
  editingUser.value = user
  form.value = { name: user.name_user, surname: user.surname_user, username: user.username_user, password: '' }
  formError.value = ''
  formDialog.value?.showModal()
}

async function onSubmit() {
  formError.value = ''
  submitting.value = true

  try {
    if (editingUser.value) {
      const payload = { name: form.value.name, surname: form.value.surname, username: form.value.username }
      if (form.value.password) payload.password = form.value.password

      await updateUser(editingUser.value.id_user, payload)
      toast.success('Usuario actualizado.')
    } else {
      await createUser(form.value)
      toast.success('Usuario creado.')
    }

    formDialog.value?.close()
    await load()
  } catch (error) {
    formError.value = error.response?.data?.detail?.[0]?.msg
      ?? error.response?.data?.detail
      ?? 'No se pudo guardar el usuario.'
  } finally {
    submitting.value = false
  }
}

function askDelete(user) {
  pendingDeleteId.value = user.id_user
  confirmDialog.value?.open()
}

async function onConfirmDelete() {
  try {
    await deleteUser(pendingDeleteId.value)
    toast.success('Usuario desactivado.')
    await load()
  } catch {
    toast.error('No se pudo eliminar el usuario.')
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-ink">Usuarios</h1>
        <p class="mt-1 text-sm text-ink-secondary">
          Administrá las cuentas del sistema y sus credenciales de acceso.
        </p>
      </div>
      <button
        type="button"
        class="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-ink transition active:scale-[0.98]"
        @click="openCreate"
      >
        <PhPlus class="size-4" aria-hidden="true" />
        Nuevo usuario
      </button>
    </div>

    <div class="mt-6">
      <DataTable
        :columns="columns"
        :rows="users"
        row-key="id_user"
        :loading="loading"
        empty-message="Todavía no hay usuarios registrados."
      >
        <template #cell-estado="{ row }">
          <StatusBadge :estado="row.estado" />
        </template>

        <template #actions="{ row }">
          <button
            type="button"
            class="rounded-lg p-2 text-ink-secondary transition hover:bg-ink/5 hover:text-ink"
            aria-label="Editar usuario"
            @click="openEdit(row)"
          >
            <PhPencilSimple class="size-4" aria-hidden="true" />
          </button>
          <button
            type="button"
            class="rounded-lg p-2 text-ink-secondary transition hover:bg-danger/10 hover:text-danger"
            aria-label="Eliminar usuario"
            @click="askDelete(row)"
          >
            <PhTrash class="size-4" aria-hidden="true" />
          </button>
        </template>
      </DataTable>
    </div>

    <dialog ref="formDialog" class="z-modal w-full max-w-md rounded-xl border border-border bg-surface p-0 text-ink backdrop:bg-ink/40">
      <form class="p-6" novalidate @submit.prevent="onSubmit">
        <h2 class="text-base font-semibold">{{ editingUser ? 'Editar usuario' : 'Nuevo usuario' }}</h2>

        <div class="mt-4 flex flex-col gap-4">
          <div class="flex flex-col gap-1.5">
            <label for="name" class="text-sm font-medium">Nombre</label>
            <input id="name" v-model="form.name" required class="rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-accent" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label for="surname" class="text-sm font-medium">Apellido</label>
            <input id="surname" v-model="form.surname" required class="rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-accent" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label for="username" class="text-sm font-medium">Usuario</label>
            <input id="username" v-model="form.username" required class="rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-accent" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label for="password" class="text-sm font-medium">
              Contraseña {{ editingUser ? '(dejar vacío para no cambiar)' : '' }}
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              :required="!editingUser"
              class="rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-accent"
            />
            <ul v-if="form.password" class="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs">
              <li :class="passwordChecks.length ? 'text-success' : 'text-ink-muted'">≥ 8 caracteres</li>
              <li :class="passwordChecks.upper ? 'text-success' : 'text-ink-muted'">Una mayúscula</li>
              <li :class="passwordChecks.lower ? 'text-success' : 'text-ink-muted'">Una minúscula</li>
              <li :class="passwordChecks.digit ? 'text-success' : 'text-ink-muted'">Un número</li>
            </ul>
          </div>

          <p v-if="formError" class="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger" role="alert">
            {{ formError }}
          </p>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button type="button" class="rounded-lg px-4 py-2 text-sm font-medium text-ink-secondary hover:bg-ink/5" @click="formDialog?.close()">
            Cancelar
          </button>
          <button type="submit" :disabled="submitting" class="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-ink transition active:scale-[0.98] disabled:opacity-60">
            Guardar
          </button>
        </div>
      </form>
    </dialog>

    <ConfirmDialog
      ref="confirmDialog"
      title="Eliminar usuario"
      message="El usuario quedará inactivo y dejará de poder iniciar sesión. Esta acción se puede revertir solo desde la base de datos."
      confirm-label="Eliminar"
      @confirm="onConfirmDelete"
    />
  </div>
</template>
