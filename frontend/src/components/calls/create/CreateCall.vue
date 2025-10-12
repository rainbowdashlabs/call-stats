<script setup lang="ts">
import {onMounted, ref} from "vue";
import {listSubjects} from "@/../../../api/subjects.ts";
import type {MultiSelectGroup, MultiSelectItem} from "../../../interfaces/Subject.ts";

const subjects = ref<MultiSelectGroup[]>([])
const chosen = ref<MultiSelectItem[]>([])

onMounted(async () => {
  subjects.value = await listSubjects()
})
</script>

<template>
  <input type="datetime-local" placeholder="start" class="bg-gray-800 text-gray-50"/>
  <input type="datetime-local" placeholder="end" class="bg-gray-800 text-gray-50"/>

  <div v-for="item in chosen" :key="item.label">
    {{ item }}
  </div>

  <div v-for="item in subjects" :key="item.label">
    <SubjectGroupButton v-bind:group/>
  </div>
</template>

<style scoped>

</style>
