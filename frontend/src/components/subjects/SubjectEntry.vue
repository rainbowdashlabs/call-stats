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

const original = ref<MultiSelectItem>()

const removed = ref(false)
const renaming = ref(false)

function toggleRename() {
  if (!renaming.value) {
    original.value = Object.assign({}, props.subject)
  }
  renaming.value = !renaming.value
}

function cancelRename() {
  props.subject!.label = original.value!.label
  toggleRename()
}

async function rename() {
  await updateSubject(props.subject!.value! as number, {
    id: props.subject!.value! as number,
    name: props.subject?.label,
    group: props.group
  })
  toggleRename()
}

async function remove() {
  removed.value = true
  await deleteSubject(props.subject?.value! as number)
}

function confirm(event: KeyboardEvent) {
  console.log(event.key)
  if (event.key === "Enter") {
    rename()
  }
  if (event.key === "Escape") {
    cancelRename()
  }
}

</script>

<template>

  <div v-if="removed" class="bg-red-500">
    {{ subject.label }}
  </div>
  <div v-else-if="renaming" class="flex gap-2 bg-yellow-500">
    <input class="grow" type="text" v-model="subject.label" @keydown="confirm"/>
    <div class="flex gap-2">
      <div @click="rename" style="cursor: pointer">✔️</div>
      <div @click="cancelRename" style="cursor: pointer">❌</div>
    </div>
  </div>
  <div v-else class="flex gap-2 justify-center">
    <div class="grow">{{ subject.label }}</div>
    <div class="flex gap-2">
      <div @click="remove" style="cursor: pointer" class="justify-items-end">🗑️</div>
      <div @click="toggleRename" style="cursor: pointer" class="justify-items-end">✏️</div>
    </div>
  </div>

</template>

<style scoped>

</style>
