<script setup lang="ts">
import {type PropType, ref} from "vue";
import type {MultiSelectItem} from "../../interfaces/Subject.ts";
import {deleteSubject, updateSubject} from "../../api/subjects.ts";

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

const removed = ref(false)
const renaming = ref(false)
const editLabel = ref('')

function startRename() {
  editLabel.value = props.subject.label
  renaming.value = true
}

function cancelRename() {
  renaming.value = false
}

async function rename() {
  await updateSubject(props.subject.value as number, {
    id: props.subject.value as number,
    name: editLabel.value,
    group: props.group
  })
  props.subject.label = editLabel.value
  renaming.value = false
}

async function remove() {
  removed.value = true
  await deleteSubject(props.subject.value as number)
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Enter") rename()
  if (event.key === "Escape") cancelRename()
}
</script>

<template>
  <div v-if="removed" class="bg-red-500 px-2 py-1 rounded">
    {{ subject.label }}
  </div>
  <div v-else-if="renaming" class="flex gap-2 bg-yellow-500 px-2 py-1 rounded">
    <input class="grow bg-transparent" type="text" v-model="editLabel" @keydown="handleKeydown"/>
    <div class="flex gap-2">
      <div @click="rename" class="cursor-pointer">✔️</div>
      <div @click="cancelRename" class="cursor-pointer">❌</div>
    </div>
  </div>
  <div v-else class="flex gap-2 justify-center px-2 py-1">
    <div class="grow">{{ subject.label }}</div>
    <div class="flex gap-2">
      <div @click="remove" class="cursor-pointer">🗑️</div>
      <div @click="startRename" class="cursor-pointer">✏️</div>
    </div>
  </div>
</template>
