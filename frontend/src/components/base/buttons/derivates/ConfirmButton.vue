<script setup lang="ts">
import StandardButton from "../StandardButton.vue";

defineProps({
  disabled: {type: Boolean, default: false}
})
defineEmits(['click'])
</script>

<template>
  <StandardButton class="primary" @click="$emit('click')" :disabled="disabled">
    <slot/>
  </StandardButton>
</template>

<style scoped>
.primary {
  background: var(--c-action);
  border-color: var(--c-action);
  color: var(--c-action-ink);
}

.primary:hover:not(:disabled) {
  opacity: 0.88;
  background: var(--c-action);
}
</style>
