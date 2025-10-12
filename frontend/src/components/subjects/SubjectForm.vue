<script setup lang="ts">
const emit = defineEmits(['create'])

let group: String | null = '';
let name: String | null = '';


</script>

<template>

  <col span="2">
  <input v-model="group" placeholder="group" class="bg-gray-800 text-gray-50" type="text"/>
  <input v-model="name" placeholder="name" class="bg-gray-800 text-gray-50" type="text"/>
  <button @click="emit('create', {name: 'test'})">Create</button>
</template>

<style scoped>

</style>
