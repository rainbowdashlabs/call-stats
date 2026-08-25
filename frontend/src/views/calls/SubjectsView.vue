<script setup lang="ts">
import {onMounted, ref, watch} from 'vue'
import SubjectForm from '../../components/subjects/SubjectForm.vue'
import type {MultiSelectGroup, Subject} from '../../interfaces/Subject'
import {createSubject, listSubjects} from '../../api/subjects'
import SubjectList from "../../components/subjects/SubjectList.vue";
import {t} from "../../i18n";

const subjects = ref<MultiSelectGroup[]>([])
const showArchived = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    subjects.value = await listSubjects(true, showArchived.value) as MultiSelectGroup[]
  } catch (e: any) {
    error.value = e?.message ?? t('errors.subjectsLoad')
  } finally {
    loading.value = false
  }
}

watch(showArchived, () => load())

async function handleCreate(subject: Subject) {
  try {
    const created = await createSubject(subject)
    let found = false
    for (let group of subjects.value) {
      if (group.label == created.group) {
        group.items.push({label: created.name, value: created.id!})
        found = true
        break
      }
    }
    if (!found) {
      subjects.value.push({label: created.group, items: [{label: created.name, value: created.id!}]})
    }
  } catch (e: any) {
    alert(e?.message ?? t('errors.subjectCreate'))
  }
}

onMounted(load)

</script>

<template>
  <SubjectForm @create="handleCreate"/>
  <label class="flex items-center gap-2 my-2 text-sm text-gray-400">
    <input type="checkbox" v-model="showArchived"/>
    {{ t('subjects.showArchived') }}
  </label>
  <div v-if="loading" class="p-2">{{ t('common.loading') }}</div>
  <div v-else-if="error" class="p-2 text-red-400">{{ error }}</div>
  <SubjectList v-else :subject_groups="subjects" @removed="load"/>
  <p class="text-xs text-gray-500 mt-4">{{ t('subjects.archiveHint') }}</p>
</template>

<style scoped>
.subjects-view {
  display: grid;
  gap: 1rem;
}

header h1 {
  font-size: 1.5rem;
  font-weight: 700;
}

.error {
  color: #b91c1c;
}
</style>
