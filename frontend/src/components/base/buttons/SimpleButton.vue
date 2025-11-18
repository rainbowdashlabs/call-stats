<script setup lang="ts">
defineEmits(["click"])
</script>

<template>
  <div class="cursor-pointer" @click="$emit('click')">
    <slot/>
  </div>
</template>

<style scoped>
</style>