<script setup lang="ts">
defineProps({
  disabled: { type: Boolean, default: false }
})
defineEmits(["click"])
</script>

<template>
  <button type="button" class="text-gray-900 m-1 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="disabled" @click="$emit('click')">
    <slot/>
  </button>
</template>

<style scoped>

</style>
