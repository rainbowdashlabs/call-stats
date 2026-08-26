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
  <section class="flex flex-col gap-6">
    <header>
      <div class="eyebrow">{{ t('calls.eyebrow') }}</div>
      <h1 class="headline text-4xl mt-1">{{ t('subjects.title') }}</h1>
    </header>

    <div class="card p-5">
      <SubjectForm @create="handleCreate"/>
    </div>

    <label class="flex items-center gap-2 w-fit cursor-pointer">
      <input type="checkbox" v-model="showArchived"/>
      <span class="label">{{ t('subjects.showArchived') }}</span>
    </label>

    <div v-if="loading" class="p-8 text-center text-muted">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="p-8 text-center" style="color: var(--c-signal-ink)">{{ error }}</div>
    <SubjectList v-else :subject_groups="subjects" @removed="load"/>

    <p class="text-xs text-muted max-w-prose">{{ t('subjects.archiveHint') }}</p>
  </section>
</template>
