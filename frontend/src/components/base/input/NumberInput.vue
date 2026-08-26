<script setup lang="ts">
const model = defineModel({type: Number})
</script>

<template>
  <input type="number" v-model="model" class="field tabular"/>
</template>
