<script setup lang="ts">
defineProps({
  placeholder: {type: String, default: ''}
})
const model = defineModel({type: String})
</script>

<template>
  <input type="text" v-model="model" :placeholder="placeholder" class="field"/>
</template>
