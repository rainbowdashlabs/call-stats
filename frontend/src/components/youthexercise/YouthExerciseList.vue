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
  <section class="card">
    <div class="flex items-baseline justify-between px-5 pt-4 pb-3 border-b border-rule">
      <h2 class="headline text-xl">{{ t('youth.title') }}</h2>
      <label class="flex items-center gap-2">
        <span class="label">{{ t('common.perPage') }}</span>
        <select v-model="pageSize" class="field tabular" style="height: 30px; width: auto; padding: 0 6px;">
          <option v-for="i in [5, 10, 20, 50]" :value="i">{{ i }}</option>
        </select>
      </label>
    </div>

    <div class="list-head">
      <span class="label">{{ t('common.topic') }}</span>
      <span class="label">{{ t('common.date') }}</span>
      <span class="label text-right">{{ t('common.duration') }}</span>
      <span class="label text-right">{{ t('common.participants') }}</span>
      <span class="label text-right">{{ t('common.instructors') }}</span>
    </div>

    <div v-if="loading" class="p-8 text-center text-muted">{{ t('common.loading') }}</div>
    <div v-else-if="entries.length === 0" class="p-8 text-center text-muted">{{ t('youth.empty') }}</div>
    <div v-else v-for="exercise in entries" :key="exercise.id" class="list-row">
      <span class="truncate font-medium">{{ exercise.subject }}</span>
      <span class="tabular text-sm">{{ formatDate(exercise.exercise_date) }}</span>
      <span class="tabular text-sm text-right">{{ formatDuration(exercise.duration) }}</span>
      <span class="tabular text-sm text-right">{{ exercise.participants }}</span>
      <span class="tabular text-sm text-right">{{ exercise.instructors.length }}</span>
    </div>

    <div class="px-5 py-3 border-t border-rule">
      <Navigation :pages="pages" v-model="page"/>
    </div>
  </section>
</template>

<style scoped>
.list-head, .list-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 110px 80px 84px 84px;
  gap: 16px;
  padding: 11px 18px;
  align-items: center;
}

.list-head {
  background: var(--c-raised);
  padding-top: 9px;
  padding-bottom: 9px;
}

.list-row {
  border-top: 1px solid var(--c-hairline);
}
</style>
