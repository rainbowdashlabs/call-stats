<script setup lang="ts">
import SmartSelect from "../base/select/SmartSelect.vue";
import {onMounted, ref} from "vue";
import {listSubjects} from "../../api/subjects.ts";
import type {MultiSelectGroup} from "../../interfaces/Subject.ts";
import TextInput from "../base/input/TextInput.vue";

const emit = defineEmits(['create'])

const group = ref<string | null>('');
const name = ref<string | null>('');
const groups = ref<string[]>([])

async function load() {
  let subjects: MultiSelectGroup[] = (await listSubjects(true)) as MultiSelectGroup[]
  groups.value = subjects.map(e => e.label)

  groups.value = await fetch('/api/groups').then(r => r.json())
}

onMounted(load)

function create() {
  console.log({group: group.value, name: name.value})
  emit("create", {group: group.value, name: name.value})
  group.value = ''
  name.value = ''
}

</script>

<template>
  <div class="grid grid-cols-3 gap-2">
    <SmartSelect :options="groups" :value_mapper="(v) => v!" :key_mapper="(k) => k" :suggestions="groups"
                 v-model="group" placeholder="group"/>
    <TextInput :v-model="name" placeholder="name" class="bg-gray-800 text-gray-50 w-full px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500" type="text"/>
    <button @click="create">Create</button>
  </div>
</template>

<style scoped>

</style>
