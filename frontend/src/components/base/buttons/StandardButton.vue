<script setup lang="ts">
defineEmits(["click"])
</script>

<template>
  <button type="button" class="text-gray-900 m-1" @click="$emit('click')">
    <slot/>
  </button>
</template>

<style scoped>

</style>
