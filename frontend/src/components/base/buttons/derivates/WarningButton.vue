<script setup lang="ts">
import StandardButton from "../StandardButton.vue";

defineProps({
  disabled: {type: Boolean, default: false}
})
defineEmits(['click'])
</script>

<template>
  <StandardButton @click="$emit('click')" :disabled="disabled">
    <slot/>
  </StandardButton>
</template>
