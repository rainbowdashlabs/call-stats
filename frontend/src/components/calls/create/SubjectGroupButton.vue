<script setup lang="ts">
import {ref} from "vue";
import StandardButton from "../../base/buttons/StandardButton.vue";
import type {MultiSelectGroup} from "../../../interfaces/Subject.ts";

defineProps({
  group: MultiSelectGroup
})

const active = ref(false)
</script>

<template>
  <div v-if="active">
    <StandardButton @click="active = false">{{ group.label }}</StandardButton>
  </div>
  <div v-else v-for="item in group.items" :key="item.id">
    {{ item }}
  </div>
</template>

<style scoped>

</style>
