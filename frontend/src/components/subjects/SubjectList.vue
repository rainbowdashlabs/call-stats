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

</script>

<template>

  <SubjectGroup v-for="item in subject_groups" :group="item"/>

</template>

<style scoped>

</style>
