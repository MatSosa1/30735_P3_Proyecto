<script setup>
import { ref } from 'vue'
import { PhCaretDown, PhCaretRight } from '@phosphor-icons/vue'
import SidebarNode from './SidebarNode.vue'

const props = defineProps({
  node: { type: Object, required: true },
  depth: { type: Number, default: 0 },
})

// Los grupos (sin url_module) arrancan expandidos: son pocos niveles y el usuario debe poder
// ver de entrada a qué tiene acceso, sin clicks extra.
const expanded = ref(true)
const isLeaf = Boolean(props.node.url_module)
</script>

<template>
  <li>
    <RouterLink
      v-if="isLeaf"
      :to="`/app${node.url_module}`"
      class="flex items-center rounded-lg px-3 py-2 text-sm text-ink-secondary transition hover:bg-ink/5 hover:text-ink"
      active-class="bg-accent/10 text-accent font-medium"
      :style="{ paddingLeft: `${0.75 + depth * 1}rem` }"
    >
      {{ node.name_module }}
    </RouterLink>

    <button
      v-else
      type="button"
      class="flex w-full items-center gap-1.5 rounded-lg px-3 py-2 text-left text-sm font-medium text-ink-secondary hover:bg-ink/5"
      :style="{ paddingLeft: `${0.75 + depth * 1}rem` }"
      :aria-expanded="expanded"
      @click="expanded = !expanded"
    >
      <component :is="expanded ? PhCaretDown : PhCaretRight" class="size-3.5 shrink-0" aria-hidden="true" />
      {{ node.name_module }}
    </button>

    <ul v-if="!isLeaf && expanded && node.children?.length">
      <SidebarNode
        v-for="child in node.children"
        :key="child.id_module"
        :node="child"
        :depth="depth + 1"
      />
    </ul>
  </li>
</template>
