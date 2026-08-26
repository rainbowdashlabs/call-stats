<script setup lang="ts">
import SmartSelect from "../base/select/SmartSelect.vue";
import {onMounted, ref} from "vue";
import {listSubjects} from "../../api/subjects.ts";
import type {MultiSelectGroup} from "../../interfaces/Subject.ts";
import TextInput from "../base/input/TextInput.vue";
import {t} from "../../i18n";
import ConfirmButton from "../base/buttons/derivates/ConfirmButton.vue";

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
  <div class="flex flex-col gap-3">
    <span class="label">{{ t('subjects.newSubject') }}</span>
    <div class="grid grid-cols-1 md:grid-cols-[1fr_1fr_auto] gap-3">
      <SmartSelect :options="groups" :value-mapper="(v) => v" :key-mapper="(k) => k"
                   :generator="(v:string) => v" v-model="group" :placeholder="t('subjects.group')"/>
      <TextInput v-model="name" :placeholder="t('subjects.name')"/>
      <ConfirmButton :disabled="!group || !name" @click="create">
        <font-awesome-icon icon="fa-solid fa-plus"/>
        {{ t('common.create') }}
      </ConfirmButton>
    </div>
  </div>
</template>
