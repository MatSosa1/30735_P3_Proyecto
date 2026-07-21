<script setup>
import { PhTreeStructure } from '@phosphor-icons/vue'
import { useAuthStore } from '../stores/auth'
import SidebarNode from './SidebarNode.vue'

const auth = useAuthStore()
</script>

<template>
  <nav class="flex h-full w-64 shrink-0 flex-col border-r border-border bg-surface p-4" aria-label="Menú principal">
    <div class="flex items-center gap-2 px-2 pb-4 text-sm font-semibold text-ink">
      <PhTreeStructure class="size-5 text-accent" aria-hidden="true" />
      Master Gateway
    </div>

    <ul class="flex flex-col gap-0.5">
      <SidebarNode v-for="node in auth.menuTree" :key="node.id_module" :node="node" />
    </ul>
  </nav>
</template>
