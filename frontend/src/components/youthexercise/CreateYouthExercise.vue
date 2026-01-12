<script setup lang="ts">
import {onMounted, ref, watch} from "vue";
import type {Member} from "../../interfaces/Member.ts";
import {ADateTime} from "../../scripts/datetime.ts";
import ButtonMultiSelect from "../base/select/ButtonMultiSelect.vue";
import {listMembers} from "../../api/members.ts";
import DatePicker from "../base/datetime/DatePicker.vue";
import TextInput from "../base/input/TextInput.vue";
import NumberInput from "../base/input/NumberInput.vue";
import {addYouthExerciseMembers, createYouthExercise} from "../../api/youthExercises.ts";

const members = ref<Member[]>([])
const selectedMembers = ref<Member[]>([])
const subject = ref('')
const date = ref<ADateTime>(ADateTime.now())
const hours = ref<number>(3)
const minutes = ref<number>(0)
const participants = ref<number>(0)

onMounted(async () => {
  members.value = await listMembers(true, date.value.toUnixTimestamp())
})

async function submit() {
  let exercise_date = date.value.toUnixTimestamp()
  let exercise = await createYouthExercise({
    subject: subject.value,
    exercise_date: exercise_date,
    duration: minutes.value + hours.value * 60,
    participants: participants.value
  })
  await addYouthExerciseMembers(exercise, selectedMembers.value.map(e => e.id!))
  selectedMembers.value = []
  subject.value = ''
  hours.value = 3
  minutes.value = 0
  participants.value = 0
}

watch(() => date.value.toUnixTimestamp(), async (_, newDate) => {
  members.value = await listMembers(true, newDate)
});
</script>

<template>
  <div class="flex flex-col gap-2">
    Thema
    <TextInput v-model="subject"/>
    <div class="flex gap-2">
      <div>
        Datum
        <DatePicker :model-value="date"/>
      </div>
      <div>
        Stunden
        <NumberInput v-model="hours"/>
      </div>
      <div>
        Minuten
        <NumberInput v-model="minutes"/>
      </div>
      <div>
        Teilnehmer
        <NumberInput v-model="participants"/>
      </div>
    </div>
    <div v-if="subject">
      Members
      <ButtonMultiSelect v-model="selectedMembers" :options="members" :value_mapper="(e:Member) => e.name"
                         :key_mapper="(e:Member) => e.id" :show_empty="false"/>
    </div>

    <button @click="submit" class="bg-green-500 text-white p-2">Create</button>
  </div>


</template>

<style scoped>

</style>