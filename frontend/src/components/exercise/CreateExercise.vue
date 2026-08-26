<script setup lang="ts">
import {computed, onMounted, ref, watch} from "vue";
import type {Member} from "../../interfaces/Member.ts";
import {ADateTime} from "../../scripts/datetime.ts";
import ButtonMultiSelect from "../base/select/ButtonMultiSelect.vue";
import {listMembers} from "../../api/members.ts";
import {addExerciseMembers, createExercise} from "../../api/exercises.ts";
import {emitSuccess} from "../../events/bus.ts";
import DatePicker from "../base/datetime/DatePicker.vue";
import TextInput from "../base/input/TextInput.vue";
import NumberPicker from "../base/datetime/NumberPicker.vue";
import {t} from "../../i18n";
import ConfirmButton from "../base/buttons/derivates/ConfirmButton.vue";

const members = ref<Member[]>([])
const selectedMembers = ref<Member[]>([])
const subject = ref('')
const date = ref<ADateTime>(ADateTime.now())
const hours = ref<number>(3)
const minutes = ref<number>(0)
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
    let exercise = await createExercise({
      subject: subject.value,
      exercise_date: exercise_date,
      duration: minutes.value + hours.value * 60
    })
    await addExerciseMembers(exercise, selectedMembers.value.map(e => e.id!))
    emitSuccess(t('exercises.created'))
    selectedMembers.value = []
    subject.value = ''
    hours.value = 3
    minutes.value = 0
  } finally {
    submitting.value = false
  }
}

watch(() => date.value.toUnixTimestamp(), async (newDate) => {
  members.value = await listMembers(true, newDate)
});
</script>

<template>
  <section class="card p-5 flex flex-col gap-4">
    <h2 class="headline text-xl">{{ t('exercises.createTitle') }}</h2>

    <div class="flex flex-col gap-2">
      <span class="label">{{ t('common.topic') }}</span>
      <TextInput v-model="subject"/>
    </div>

    <div class="flex flex-wrap items-end gap-6">
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('common.date') }}</span>
        <DatePicker v-model="date"/>
      </div>
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('common.hours') }}</span>
        <NumberPicker :min="0" :max="24" v-model="hours"/>
      </div>
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('common.minutes') }}</span>
        <NumberPicker :min="0" :max="59" v-model="minutes"/>
      </div>
      
    </div>

    <div v-if="subject" class="flex flex-col gap-2">
      <span class="label">{{ t('common.participants') }}</span>
      <ButtonMultiSelect v-model="selectedMembers" :options="members" :value-mapper="(e:Member) => e.name"
                         :key-mapper="(e:Member) => e.id"/>
    </div>

    <div>
      <ConfirmButton :disabled="!canSubmit" @click="submit">
        <font-awesome-icon icon="fa-solid fa-plus"/>
        {{ t('common.create') }}
      </ConfirmButton>
    </div>
  </section>
</template>
