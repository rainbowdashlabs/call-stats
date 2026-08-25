<script setup lang="ts">
import {computed, onMounted, ref, watch} from "vue";
import type {Member} from "../../interfaces/Member.ts";
import {ADateTime} from "../../scripts/datetime.ts";
import ButtonMultiSelect from "../base/select/ButtonMultiSelect.vue";
import {listMembers} from "../../api/members.ts";
import DatePicker from "../base/datetime/DatePicker.vue";
import TextInput from "../base/input/TextInput.vue";
import NumberInput from "../base/input/NumberInput.vue";
import {addYouthExerciseMembers, createYouthExercise} from "../../api/youthExercises.ts";
import {emitSuccess} from "../../events/bus.ts";
import {t} from "../../i18n";

const members = ref<Member[]>([])
const selectedMembers = ref<Member[]>([])
const subject = ref('')
const date = ref<ADateTime>(ADateTime.now())
const hours = ref<number>(3)
const minutes = ref<number>(0)
const participants = ref<number>(0)
const submitting = ref(false)

const canSubmit = computed(() => subject.value.trim().length > 0 && selectedMembers.value.length > 0 && !submitting.value)

onMounted(async () => {
  members.value = await listMembers(true, date.value.toUnixTimestamp())
})

async function submit() {
  if (!canSubmit.value) return
  submitting.value = true
  try {
    let exercise_date = date.value.toUnixTimestamp()
    let exercise = await createYouthExercise({
      subject: subject.value,
      exercise_date: exercise_date,
      duration: minutes.value + hours.value * 60,
      participants: participants.value
    })
    await addYouthExerciseMembers(exercise, selectedMembers.value.map(e => e.id!))
    emitSuccess(t('youth.created'))
    selectedMembers.value = []
    subject.value = ''
    hours.value = 3
    minutes.value = 0
    participants.value = 0
  } finally {
    submitting.value = false
  }
}

watch(() => date.value.toUnixTimestamp(), async (newDate) => {
  members.value = await listMembers(true, newDate)
});
</script>

<template>
  <div class="flex flex-col gap-2">
    {{ t('common.topic') }}
    <TextInput v-model="subject"/>
    <div class="flex gap-2">
      <div>
        {{ t('common.date') }}
        <DatePicker v-model="date"/>
      </div>
      <div>
        {{ t('common.hours') }}
        <NumberInput v-model="hours"/>
      </div>
      <div>
        {{ t('common.minutes') }}
        <NumberInput v-model="minutes"/>
      </div>
      <div>
        {{ t('common.participants') }}
        <NumberInput v-model="participants"/>
      </div>
    </div>
    <div v-if="subject">
      {{ t('common.members') }}
      <ButtonMultiSelect v-model="selectedMembers" :options="members" :value-mapper="(e:Member) => e.name"
                         :key-mapper="(e:Member) => e.id"/>
    </div>

    <button @click="submit" :disabled="!canSubmit" class="bg-green-500 text-white p-2 disabled:opacity-50 disabled:cursor-not-allowed">{{ t('common.create') }}</button>
  </div>


</template>

<style scoped>

</style>