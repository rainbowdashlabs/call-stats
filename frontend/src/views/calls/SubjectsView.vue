<script setup lang="ts">
import {onMounted, ref} from 'vue'
import SubjectForm from '../../components/subjects/SubjectForm.vue'
import type {MultiSelectGroup, Subject} from '../../interfaces/Subject'
import {createSubject, listSubjects} from '../../api/subjects'
import SubjectList from "../../components/subjects/SubjectList.vue";
import {t} from "../../i18n";

const subjects = ref<MultiSelectGroup[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    subjects.value = await listSubjects(true) as MultiSelectGroup[]
  } catch (e: any) {
    error.value = e?.message ?? t('errors.subjectsLoad')
  } finally {
    loading.value = false
  }
}

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
  <SubjectList :subject_groups="subjects"/>
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
