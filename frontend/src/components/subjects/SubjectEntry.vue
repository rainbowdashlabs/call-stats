<script setup lang="ts">
import {type PropType, ref} from "vue";
import type {MultiSelectItem} from "../../interfaces/Subject.ts";
import {deleteSubject, updateSubject} from "../../api/subjects.ts";
import {t} from "../../i18n";
import SimpleButton from "../base/buttons/SimpleButton.vue";

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
  <div v-if="renaming" class="subject-row">
    <input class="field" type="text" v-model="editLabel" @keydown="handleKeydown"/>
    <div class="flex gap-1">
      <SimpleButton @click="rename" :aria-label="t('common.save')">
        <font-awesome-icon icon="fa-solid fa-check"/>
      </SimpleButton>
      <SimpleButton @click="cancelRename" :aria-label="t('common.cancel')">
        <font-awesome-icon icon="fa-solid fa-xmark"/>
      </SimpleButton>
    </div>
  </div>
  <div v-else class="subject-row" :class="{archived: subject.archived}">
    <div class="min-w-0">
      <div class="truncate">{{ subject.label }}</div>
      <span v-if="subject.archived" class="label">{{ t('subjects.archived') }}</span>
    </div>
    <div class="flex gap-1 shrink-0">
      <SimpleButton @click="toggleArchived"
                    :aria-label="subject.archived ? t('subjects.restore') : t('subjects.archive')">
        <font-awesome-icon :icon="subject.archived ? 'fa-solid fa-rotate-left' : 'fa-solid fa-box-archive'"/>
      </SimpleButton>
      <SimpleButton @click="startRename" :aria-label="t('subjects.rename')">
        <font-awesome-icon icon="fa-solid fa-pen"/>
      </SimpleButton>
      <SimpleButton class="danger" @click="remove" :aria-label="t('common.delete')">
        <font-awesome-icon icon="fa-solid fa-trash"/>
      </SimpleButton>
    </div>
  </div>
</template>

<style scoped>
.subject-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 9px 16px;
  border-top: 1px solid var(--c-hairline);
}

.subject-row.archived {
  color: var(--c-muted);
}

.danger:hover {
  color: var(--c-signal);
}
</style>
