<script setup lang="ts">
import {onMounted, ref} from "vue";
import type {Subject} from "../../../interfaces/Subject.ts";
import {listSubjects} from "../../../api/subjects.ts";
import {listMembers} from "../../../api/members.ts";
import type {Member} from "../../../interfaces/Member.ts";
import SmartMultiSelect from "../../base/select/SmartMultiSelect.vue";
import {createCall} from "../../../api/calls.ts";
import {ADateTime} from "../../../scripts/datetime.ts";
import DateTimePicker from "../../base/datetime/DateTimePicker.vue";
import TimePicker from "../../base/datetime/TimePicker.vue";

const subjects = ref<Subject[]>([])
const chosenSubjects = ref<Subject[]>([])
const members = ref<Member[]>([])
const selectedMembers = ref<Member[]>([])
const abort_reason = ref<string | null>(null)
const note = ref<string | null>(null)
const additional = ref<number>(0)
const start = ref<ADateTime>(ADateTime.now())
const end = ref<ADateTime>(ADateTime.now())

onMounted(async () => {
  subjects.value = await listSubjects(false) as Subject[]
  members.value = await listMembers(true)
})


async function submit() {

  end.value = end.value.applyDate(start.value)
  if (start.value.toUnixTimestamp() > end.value.toUnixTimestamp()) {
    end.value = end.value.nextDay()
  }
  console.log("start: " + start.value)
  console.log("end: " + end.value)

  await createCall({
    subjects: chosenSubjects.value.map(e => e.id!),
    start: start.value.toUnixTimestamp(),
    end: end.value.toUnixTimestamp(),
    additional: additional.value,
    members: selectedMembers.value.map(e => e.id!),
    note: note.value,
    abort_reason: abort_reason.value
  })
  chosenSubjects.value = []
  selectedMembers.value = []
  abort_reason.value = null
  note.value = null
  additional.value = 0
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <div class="text-2xl">Create Call</div>
    <div>
      Stichwort
      <SmartMultiSelect v-model="chosenSubjects" :options="subjects" :value_mapper="(e:Subject) => e.name"
                        :key_mapper="(e: Subject) => e.id!" :show_empty="false"/>
    </div>

    <div class="flex justify-stretch gap-5">
      <div class="gap-2">
        <span>Start</span>
        <DateTimePicker v-model="start"/>
      </div>
      <div class="gap-2">
        <span>Ende</span>
        <TimePicker v-model="end"/>
      </div>
    </div>

    <div class="flex gap-2">
      Nachbereitung: <input type="number" step="1" v-model="additional" :min="0">
    </div>

    <div>
      Mitglieder
      <SmartMultiSelect v-model="selectedMembers" :options="members" :value_mapper="(e:Member) => e.name"
                        :key_mapper="(e:Member) => e.id" :show_empty="false"/>
    </div>

    <div>
      Grund bei Abbruch
      <input v-model="abort_reason" type="text" placeholder="abort_reason" class="bg-gray-800 text-gray-50 w-full"/>
    </div>

    <div>
      Notiz
      <input v-model="note" type="text" placeholder="note" class="bg-gray-800 text-gray-50 w-full"/>
    </div>

    <button @click="submit" class="bg-green-500 text-white p-2" @keydown.ctrl.enter="submit">Erstellen</button>
  </div>
</template>

<style scoped>

</style>
