<script setup lang="ts">

import type {PropType} from "vue";
import type {MultiSelectGroup} from "../../interfaces/Subject.ts";
import SubjectGroup from "./SubjectGroup.vue";

defineProps({
  subject_groups: {
    type: Object as PropType<MultiSelectGroup[]>,
    required: true
  }
})

defineEmits<{
  (e: 'removed', id: number | string): void
}>()

</script>

<template>
  <div class="flex flex-col gap-4">
    <SubjectGroup v-for="item in subject_groups" :key="item.label" :group="item"
                  @removed="id => $emit('removed', id)"/>
  </div>
</template>
