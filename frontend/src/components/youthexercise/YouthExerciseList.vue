<script setup lang="ts">
import {onMounted, ref, watch} from "vue";
import type {FullYouthExercise} from "../../interfaces/YouthExercise.ts";
import {listYouthExercises} from "../../api/youthExercises.ts";
import Navigation from "../base/pagination/Navigation.vue";
import {formatDate} from "../../scripts/datetime.ts";
import {t} from "../../i18n";

const page = ref(1)
const pageSize = ref(20)
const pages = ref(1)
const entries = ref<FullYouthExercise[]>([])
const loading = ref(false)

watch(page, () => load())
watch(pageSize, () => {
  page.value = 1
  load()
})

async function load() {
  loading.value = true
  try {
    let result = await listYouthExercises(page.value, pageSize.value)
    entries.value = result.entries
    pages.value = result.pages
    page.value = result.page
  } finally {
    loading.value = false
  }
}

function formatDuration(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m > 0 ? `${h}h ${m}m` : `${h}h`
}

onMounted(load)

defineExpose({load})
</script>

<template>
  <div class="mt-4">
    <div class="flex justify-between items-center mb-2">
      <div class="text-2xl">{{ t('youth.title') }}</div>
      <div class="flex items-center gap-2">
        <span>{{ t('common.perPage') }}</span>
        <select v-model="pageSize">
          <option v-for="i in [5, 10, 20, 50]" :value="i">{{ i }}</option>
        </select>
      </div>
    </div>

    <Navigation :pages="pages" v-model="page"/>

    <div class="border-2 rounded-2xl border-accent grid grid-cols-1 gap-2 p-2 mt-2 mb-2">
      <div class="grid grid-cols-5 gap-2 highlight rounded-2xl font-bold">
        <div>{{ t('common.topic') }}</div>
        <div>{{ t('common.date') }}</div>
        <div>{{ t('common.duration') }}</div>
        <div>{{ t('common.participants') }}</div>
        <div>{{ t('common.instructors') }}</div>
      </div>
      <div v-if="loading" class="text-center p-4">{{ t('common.loading') }}</div>
      <div v-else-if="entries.length === 0" class="text-center p-4">{{ t('youth.empty') }}</div>
      <div v-else v-for="exercise in entries" class="grid grid-cols-5 gap-2 rounded-2xl">
        <div>{{ exercise.subject }}</div>
        <div>{{ formatDate(exercise.exercise_date) }}</div>
        <div>{{ formatDuration(exercise.duration) }}</div>
        <div>{{ exercise.participants }}</div>
        <div>{{ exercise.instructors.map(m => m.name).join(', ') }}</div>
      </div>
    </div>

    <Navigation :pages="pages" v-model="page"/>
  </div>
</template>
