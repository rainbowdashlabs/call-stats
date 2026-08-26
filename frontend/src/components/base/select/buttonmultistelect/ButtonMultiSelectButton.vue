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
  <button type="button" class="pick" :class="{selected}"
          @click="selected ? $emit('deselect') : $emit('select')">
    {{ value }}
  </button>
</template>

<style scoped>
.pick {
  height: 30px;
  padding: 0 11px;
  border: 1px solid var(--c-rule);
  border-radius: 3px;
  background: var(--c-surface);
  color: var(--c-ink);
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.12s, border-color 0.12s;
}

.pick:hover {
  background: var(--c-raised);
}

.pick.selected {
  background: var(--c-action);
  border-color: var(--c-action);
  color: var(--c-action-ink);
  font-weight: 500;
}
</style>
