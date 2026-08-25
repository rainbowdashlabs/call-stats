<script setup lang="ts">
import type {PropType} from "vue";
import type {MultiSelectGroup} from "../../interfaces/Subject.ts";
import SubjectEntry from "./SubjectEntry.vue";

defineProps({
  group: {
    type: Object as PropType<MultiSelectGroup>,
    required: true
  }
})

defineEmits<{
  (e: 'removed', id: number | string): void
}>()

</script>

<template>
  {{ group.label }}
  <div class="bg-bglight border-accent rounded-xl grid grid-cols-3 gap-2">
    <SubjectEntry v-for="item in group.items" :key="item.value" :group="group.label" :subject="item"
                  @removed="id => $emit('removed', id)"/>
  </div>
</template>

<style scoped>

</style>