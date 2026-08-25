<script setup lang="ts">
defineProps<{
  value: string
  selected: boolean
}>()

defineEmits<{
  select: []
  deselect: []
}>()
</script>

<template>
  <button type="button"
          :class="selected ? 'bg-green-500 text-white' : 'bg-blue-400 text-white'"
          class="px-3 py-1 rounded transition-colors"
          @click="selected ? $emit('deselect') : $emit('select')">
    {{ value }}
  </button>
</template>
