<script setup lang="ts">
import StandardButton from "../StandardButton.vue";

defineProps({
  disabled: {type: Boolean, default: false}
})
defineEmits(['click'])
</script>

<template>
  <StandardButton class="danger" @click="$emit('click')" :disabled="disabled">
    <slot/>
  </StandardButton>
</template>

<style scoped>
.danger {
  border-color: var(--c-signal);
  color: var(--c-signal-ink);
  background: var(--c-surface);
}

.danger:hover:not(:disabled) {
  background: var(--c-signal-soft);
}
</style>
