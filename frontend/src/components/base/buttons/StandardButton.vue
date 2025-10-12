<script setup lang="ts">
defineEmits(["click"])
</script>

<template>
  <button class="bg-gray-300 text-gray-800" @click="$emit('click')">
    <slot/>
  </button>
</template>

<style scoped>

</style>
