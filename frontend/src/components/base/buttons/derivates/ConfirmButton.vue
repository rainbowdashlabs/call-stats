<script setup lang="ts">

import StandardButton from "../StandardButton.vue";

defineEmits(['click'])
</script>

<template>
  <StandardButton @click="$emit('click')" class="bg-confirm border-confirmshade">
    <slot/>
  </StandardButton>
</template>

<style scoped>

</style>