<script setup lang="ts">
import SmartSelect from "../base/select/SmartSelect.vue";
import {onMounted, ref} from "vue";
import {listSubjects} from "../../api/subjects.ts";
import type {MultiSelectGroup} from "../../interfaces/Subject.ts";
import TextInput from "../base/input/TextInput.vue";

const emit = defineEmits(['create'])

const group = ref<string>('');
const name = ref<string>('');
const groups = ref<string[]>([])

async function load() {
  const subjects: MultiSelectGroup[] = (await listSubjects(true)) as MultiSelectGroup[]
  groups.value = subjects.map(e => e.label)
}

onMounted(load)

function create() {
  if (!group.value || !name.value) return
  emit("create", {group: group.value, name: name.value})
  group.value = ''
  name.value = ''
}
</script>

<template>
  <div class="grid grid-cols-3 gap-2">
    <SmartSelect :options="groups" :value-mapper="(v) => v" :key-mapper="(k) => k"
                 v-model="group" placeholder="Gruppe"/>
    <TextInput v-model="name"/>
    <button @click="create">Create</button>
  </div>
</template>
