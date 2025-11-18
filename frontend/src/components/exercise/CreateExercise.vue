<script setup lang="ts">
import {onMounted, ref} from "vue";
import type {Member} from "../../interfaces/Member.ts";
import {parseDate, parseTime, todayDate} from "../../scripts/datetime.ts";
import SmartMultiSelect from "../base/select/SmartMultiSelect.vue";
import {listMembers} from "../../api/members.ts";
import {createExercise} from "../../api/exercises.ts";

const members = ref<Member[]>([])
const selectedMembers = ref<Member[]>([])
const subject = ref('')
const date = ref(todayDate())
const duration = ref<number>(0)

onMounted(async () => {
  members.value = await listMembers(true)
})

async function submit() {
  let exercise_date = parseDate(date.value)
  let call = await createExercise({
    subject: subject.value,
    exercise_date: exercise_date,
    duration: duration.value
  })

}

</script>

<template>
  <input type="text" v-model="subject"/>
  <input type="date" v-model="date"/>
  <input type="number" v-model="duration"/>
  <div>
    Members
    <SmartMultiSelect v-model="selectedMembers" :options="members" :value_mapper="(e:Member) => e.name"
                      :key_mapper="(e:Member) => e.id" :show_empty="false"/>
  </div>

  <button @click="submit" class="bg-green-500 text-white p-2">Create</button>



</template>

<style scoped>

</style>