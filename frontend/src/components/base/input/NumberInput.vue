<script setup lang="ts">
const model = defineModel({type: Number})
</script>

<template>
  <input
      type="number"
      v-model="model"
      class="bg-gray-800 text-gray-50 w-full px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
  />
</template>

<style scoped>

</style>