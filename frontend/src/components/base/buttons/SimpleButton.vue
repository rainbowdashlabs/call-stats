<script setup lang="ts">
defineProps({
  disabled: {type: Boolean, default: false}
})
defineEmits(["click"])
</script>

<template>
  <button type="button" class="quiet" :disabled="disabled" @click="$emit('click')">
    <slot/>
  </button>
</template>

<style scoped>
.quiet {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  border-radius: 3px;
  background: transparent;
  color: var(--c-muted);
  cursor: pointer;
  font-size: 13px;
}

.quiet:hover:not(:disabled) {
  background: var(--c-raised);
  color: var(--c-ink);
}

.quiet:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
