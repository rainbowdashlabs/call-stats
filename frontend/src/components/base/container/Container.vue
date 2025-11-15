<script setup lang="ts">


defineProps({
  color: {
    type: String,
    default: 'primary',
    required: true
  }
})

</script>

<template>

  <div class="rounded-md" :style="{borderColor: color, backgroundColor: color}">
    <slot/>
  </div>

</template>

<style scoped>

</style>