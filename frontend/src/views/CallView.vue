<script setup lang="ts">
import {useRoute} from "vue-router";
import {computed, onMounted, ref} from "vue";
import {getCall, removeCall, updateCall} from "../api/call.ts";
import type {FullCall} from "../interfaces/Call.ts";
import ErrorButton from "../components/base/buttons/derivates/ErrorButton.vue";
import SimpleButton from "../components/base/buttons/SimpleButton.vue";
import router from "../router";
import {formatDateTime} from "../scripts/datetime.ts";
import {emitSuccess} from "../events/bus.ts";
import {isAdmin} from "../auth.ts";

const route = useRoute()

const id: number = Number(route.params.id!)
const call = ref<FullCall | null>(null)

const editingNote = ref(false)
const editingAbort = ref(false)
const editNote = ref('')
const editAbort = ref('')

async function load() {
  call.value = await getCall(id)
}

const confirmDelete = ref(false)

async function remove() {
  if (!confirmDelete.value) {
    confirmDelete.value = true
    return
  }
  await removeCall(id)
  await router.push({name: "Calls"})
}

function startEditNote() {
  editNote.value = call.value?.note ?? ''
  editingNote.value = true
}

async function saveNote() {
  if (!call.value) return
  await updateCall({
    id: call.value.id,
    start: call.value.start,
    end: call.value.end,
    additional: call.value.additional,
    note: editNote.value || null,
    abort_reason: call.value.abort_reason
  })
  call.value.note = editNote.value || null
  editingNote.value = false
  emitSuccess('Notiz gespeichert.')
}

function startEditAbort() {
  editAbort.value = call.value?.abort_reason ?? ''
  editingAbort.value = true
}

async function saveAbort() {
  if (!call.value) return
  await updateCall({
    id: call.value.id,
    start: call.value.start,
    end: call.value.end,
    additional: call.value.additional,
    note: call.value.note,
    abort_reason: editAbort.value || null
  })
  call.value.abort_reason = editAbort.value || null
  editingAbort.value = false
  emitSuccess('Abbruchgrund gespeichert.')
}

const subjects = computed(() => {
  return call.value?.subjects.map(v => v.name).join(" + ")
})

const start = computed(() => {
  return call.value?.start ? formatDateTime(call.value.start as string) : ""
})

const end = computed(() => {
  return call.value?.end ? formatDateTime(call.value.end as string) : ""
})

const members = computed(() => {
  return call.value?.members.map(v => v.name).join(", ")
})

onMounted(load)
</script>

<template>
  <div v-if="call">
    <h1>{{ subjects }}</h1>

    <div>{{ start }} - {{ end }}</div>

    <div class="mt-2">{{ members }}</div>

    <div class="mt-2 flex items-center gap-2">
      <span class="font-bold">Notiz:</span>
      <div v-if="!editingNote" class="flex items-center gap-2">
        <span>{{ call.note ?? '-' }}</span>
        <SimpleButton v-if="isAdmin()" @click="startEditNote">✏️</SimpleButton>
      </div>
      <div v-else class="flex items-center gap-2">
        <input type="text" v-model="editNote" class="bg-gray-800 text-gray-50 px-2 py-1 rounded"/>
        <SimpleButton @click="saveNote">✔️</SimpleButton>
        <SimpleButton @click="editingNote = false">❌</SimpleButton>
      </div>
    </div>

    <div class="mt-2 flex items-center gap-2">
      <span class="font-bold">Abbruchgrund:</span>
      <div v-if="!editingAbort" class="flex items-center gap-2">
        <span>{{ call.abort_reason ?? '-' }}</span>
        <SimpleButton v-if="isAdmin()" @click="startEditAbort">✏️</SimpleButton>
      </div>
      <div v-else class="flex items-center gap-2">
        <input type="text" v-model="editAbort" class="bg-gray-800 text-gray-50 px-2 py-1 rounded"/>
        <SimpleButton @click="saveAbort">✔️</SimpleButton>
        <SimpleButton @click="editingAbort = false">❌</SimpleButton>
      </div>
    </div>

    <div v-if="isAdmin()" class="flex gap-2 mt-4">
      <ErrorButton @click="remove">{{ confirmDelete ? 'Wirklich loeschen?' : 'Delete' }}</ErrorButton>
      <button v-if="confirmDelete" class="bg-gray-500 text-white p-2 rounded-md" @click="confirmDelete = false">Abbrechen</button>
    </div>
  </div>
</template>
