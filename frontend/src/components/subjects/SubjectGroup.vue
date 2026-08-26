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
  <section class="card">
    <div class="px-4 py-3 border-b border-rule flex items-baseline justify-between">
      <span class="headline text-lg">{{ group.label }}</span>
      <span class="label tabular">{{ group.items.length }}</span>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      <SubjectEntry v-for="item in group.items" :key="item.value" :group="group.label" :subject="item"
                    @removed="id => $emit('removed', id)"/>
    </div>
  </section>
</template>
