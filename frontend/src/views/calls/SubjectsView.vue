<script setup lang="ts">
import {onMounted, ref} from 'vue'
import SubjectForm from '../../components/subjects/SubjectForm.vue'
import SubjectList from '../../components/subjects/SubjectList.vue'
import type {Subject} from '../../interfaces/Subject'
import {createSubject, deleteSubject, listSubjects, updateSubject} from '../../api/subjects'

const subjects = ref<Subject[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    subjects.value = await listSubjects()
  } catch (e: any) {
    error.value = e?.message ?? 'Failed to load subjects.'
  } finally {
    loading.value = false
  }
}

async function handleCreate(subject: Subject) {
  try {
    const created = await createSubject(subject)
    subjects.value = [...subjects.value, created]
  } catch (e: any) {
    alert(e?.message ?? 'Failed to create subject')
  }
}

async function handleRename(id: number, updated: Subject) {
  try {
    const saved = await updateSubject(id, updated)
    subjects.value = subjects.value.map(s => s.id === id ? saved : s)
  } catch (e: any) {
    alert(e?.message ?? 'Failed to rename subject')
  }
}

async function handleDelete(id: number) {
  if (!confirm('Delete this subject?')) return
  try {
    await deleteSubject(id)
    subjects.value = subjects.value.filter(s => s.id !== id)
  } catch (e: any) {
    alert(e?.message ?? 'Failed to delete subject')
  }
}

onMounted(load)
</script>

<template>
  <SubjectForm @create="handleCreate" />

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
