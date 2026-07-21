<script setup>
defineProps({
  columns: { type: Array, required: true }, // [{ key, label, mono }]
  rows: { type: Array, required: true },
  rowKey: { type: String, default: 'id' },
  loading: { type: Boolean, default: false },
  emptyMessage: { type: String, default: 'No hay registros todavía.' },
})
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-border bg-surface">
    <table class="w-full min-w-[560px] border-collapse text-sm">
      <thead>
        <tr class="border-b border-border text-left text-ink-secondary">
          <th v-for="column in columns" :key="column.key" class="px-4 py-3 font-medium">
            {{ column.label }}
          </th>
          <th class="px-4 py-3 text-right font-medium">Acciones</th>
        </tr>
      </thead>

      <tbody v-if="loading" class="divide-y divide-border">
        <tr v-for="n in 3" :key="n">
          <td v-for="column in columns" :key="column.key" class="px-4 py-3">
            <div class="h-4 w-24 animate-pulse rounded bg-ink/10" />
          </td>
          <td class="px-4 py-3" />
        </tr>
      </tbody>

      <tbody v-else-if="rows.length === 0">
        <tr>
          <td :colspan="columns.length + 1" class="px-4 py-10 text-center text-ink-secondary">
            {{ emptyMessage }}
            <div v-if="$slots['empty-action']" class="mt-3">
              <slot name="empty-action" />
            </div>
          </td>
        </tr>
      </tbody>

      <tbody v-else class="divide-y divide-border">
        <tr v-for="row in rows" :key="row[rowKey]">
          <td
            v-for="column in columns"
            :key="column.key"
            class="px-4 py-3"
            :class="column.mono ? 'font-mono text-[0.8125rem] text-ink-secondary' : ''"
          >
            <slot :name="`cell-${column.key}`" :row="row">
              {{ row[column.key] }}
            </slot>
          </td>
          <td class="px-4 py-3">
            <div class="flex justify-end gap-1">
              <slot name="actions" :row="row" />
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
