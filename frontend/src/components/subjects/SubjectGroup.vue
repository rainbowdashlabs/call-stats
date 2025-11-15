<script setup lang="ts">
import type {PropType} from "vue";
import type {MultiSelectGroup} from "../../interfaces/Subject.ts";
import SubjectEntry from "./SubjectEntry.vue";
import Container from "../base/container/Container.vue";

defineProps({
  group: {
    type: Object as PropType<MultiSelectGroup>,
    required: true
  }
})

</script>

<template>
  {{ group.label }}
  <div class="bg-bglight border-accent rounded-xl grid grid-cols-3 gap-2">
    <SubjectEntry v-for="item in group.items" :group="group.label" :subject="item"/>
  </div>
</template>

<style scoped>

</style>