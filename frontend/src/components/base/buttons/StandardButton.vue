<script setup lang="ts">
defineProps({
  disabled: {type: Boolean, default: false}
})
defineEmits(["click"])
</script>

<template>
  <button type="button" class="btn" :disabled="disabled" @click="$emit('click')">
    <slot/>
  </button>
</template>

<style scoped>
.btn {
  height: 38px;
  padding: 0 18px;
  border: 1px solid var(--c-rule);
  border-radius: var(--radius-control);
  background: var(--c-surface);
  color: var(--c-ink);
  font-family: var(--font-condensed);
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.15s, border-color 0.15s;
}

.btn:hover:not(:disabled) {
  background: var(--c-raised);
}

.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
