<script setup lang="ts">
defineProps({
  placeholder: { type: String, default: '' }
})
const model = defineModel({type: String})
</script>

<template>
  <input
      type="text"
      v-model="model"
      :placeholder="placeholder"
      class="bg-gray-800 text-gray-50 w-full px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
  />
</template>

<style scoped>

</style>