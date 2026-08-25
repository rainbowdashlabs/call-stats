<script setup lang="ts">
import {type PropType, ref} from "vue";
import type {MultiSelectItem} from "../../interfaces/Subject.ts";
import {deleteSubject, updateSubject} from "../../api/subjects.ts";
import {t} from "../../i18n";

const props = defineProps({
  group: {
    type: String,
    required: true
  },
  subject: {
    type: Object as PropType<MultiSelectItem>,
    required: true
  }
})

const emit = defineEmits(['removed'])

const renaming = ref(false)
const editLabel = ref('')

function startRename() {
  editLabel.value = props.subject.label
  renaming.value = true
}

function cancelRename() {
  renaming.value = false
}

function payload(overrides: object = {}) {
  return {
    id: props.subject.value as number,
    name: props.subject.label,
    group: props.group,
    archived: props.subject.archived ?? false,
    ...overrides
  }
}

async function rename() {
  await updateSubject(props.subject.value as number, payload({name: editLabel.value}))
  props.subject.label = editLabel.value
  renaming.value = false
}

async function toggleArchived() {
  const archived = !(props.subject.archived ?? false)
  await updateSubject(props.subject.value as number, payload({archived}))
  props.subject.archived = archived
}

async function remove() {
  await deleteSubject(props.subject.value as number)
  emit('removed', props.subject.value)
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Enter") rename()
  if (event.key === "Escape") cancelRename()
}
</script>

<template>
  <div v-if="renaming" class="flex gap-2 bg-yellow-500 px-2 py-1 rounded">
    <input class="grow bg-transparent" type="text" v-model="editLabel" @keydown="handleKeydown"/>
    <div class="flex gap-2">
      <div @click="rename" class="cursor-pointer">✔️</div>
      <div @click="cancelRename" class="cursor-pointer">❌</div>
    </div>
  </div>
  <div v-else class="flex gap-2 justify-center px-2 py-1" :class="subject.archived ? 'opacity-50' : ''">
    <div class="grow">
      {{ subject.label }}
      <span v-if="subject.archived" class="text-xs text-gray-400">({{ t('subjects.archived') }})</span>
    </div>
    <div class="flex gap-2">
      <div @click="toggleArchived" class="cursor-pointer"
           :title="subject.archived ? t('subjects.restore') : t('subjects.archive')">
        {{ subject.archived ? '♻️' : '📦' }}
      </div>
      <div @click="remove" class="cursor-pointer" :title="t('common.delete')">🗑️</div>
      <div @click="startRename" class="cursor-pointer" :title="t('subjects.rename')">✏️</div>
    </div>
  </div>
</template>
