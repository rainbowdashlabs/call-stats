<script setup lang="ts">
import {onMounted, ref} from "vue";
import type {Subject} from "../../../interfaces/Subject.ts";
import {listSubjects} from "../../../api/subjects.ts";
import {listMembers} from "../../../api/members.ts";
import type {Member} from "../../../interfaces/Member.ts";
import SmartMultiSelect from "../../base/select/SmartMultiSelect.vue";
import {createCall} from "../../../api/calls.ts";
import {parseTime} from "../../../scripts/datetime.ts";

const subjects = ref<Subject[]>([])
const chosenSubjects = ref<Subject[]>([])
const members = ref<Member[]>([])
const selectedMembers = ref<Member[]>([])
const start_date = ref<string>(new Date().toISOString().split('T')[0]!)
const start_time = ref<string>(new Date().toTimeString().slice(0, 5))
const end_date = ref<string>(new Date().toISOString().split('T')[0]!)
const end_time = ref<string>(new Date().toTimeString().slice(0, 5))
const abort_reason = ref<string | null>(null)
const note = ref<string | null>(null)
const additional = ref<number>(0)

onMounted(async () => {
  subjects.value = await listSubjects(false) as Subject[]
  members.value = await listMembers(true)
})


async function submit() {
  console.log("start: " + start_date.value + " " + start_time.value)
  console.log("end: " + end_date.value + " " + end_time.value)
  let start = parseTime(start_date.value!, start_time.value!)
  let end = parseTime(end_date.value!, end_time.value!)
  await createCall({
    subjects: chosenSubjects.value.map(e => e.id!),
    start: start,
    end: end,
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
      Subjects
      <SmartMultiSelect v-model="chosenSubjects" :options="subjects" :value_mapper="(e:Subject) => e.name"
                        :key_mapper="(e: Subject) => e.id!" :show_empty="false"/>
    </div>

    <div class="flex justify-stretch gap-5">
      <div class="w-full flex gap-2">
        <span>Start</span>
        <input v-model.lazy="start_date" type="date" placeholder="start_date" class="bg-gray-800 text-gray-50 w-full"
               required/>
        <input v-model.lazy="start_time" type="time" placeholder="start_time" class="bg-gray-800 text-gray-50 w-full"
               required/>
      </div>
      <div class="w-full flex gap-2">
        <span>End</span>
        <input v-model.lazy="end_date" type="date" placeholder="end_date" class="bg-gray-800 text-gray-50 w-full"/>
        <input v-model.lazy="end_time" type="time" placeholder="end_time" class="bg-gray-800 text-gray-50 w-full"/>
      </div>
    </div>

    <div class="flex gap-2">
      Additional: <input type="number" step="1" v-model="additional">
    </div>


    <div>
      Members
      <SmartMultiSelect v-model="selectedMembers" :options="members" :value_mapper="(e:Member) => e.name"
                        :key_mapper="(e:Member) => e.id" :show_empty="false"/>
    </div>

    <div>
      Abort Reason
      <input v-model="abort_reason" type="text" placeholder="abort_reason" class="bg-gray-800 text-gray-50 w-full"/>
    </div>

    <div>
      Note
      <input v-model="note" type="text" placeholder="note" class="bg-gray-800 text-gray-50 w-full"/>
    </div>

    <button @click="submit" class="bg-green-500 text-white p-2">Create</button>
  </div>
</template>

<style scoped>

</style>
