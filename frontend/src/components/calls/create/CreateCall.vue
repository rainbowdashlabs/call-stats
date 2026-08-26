<script setup lang="ts">
import {computed, onMounted, onUnmounted, ref} from "vue";
import type {Subject} from "../../../interfaces/Subject.ts";
import {listSubjects} from "../../../api/subjects.ts";
import {listMembers} from "../../../api/members.ts";
import type {Member} from "../../../interfaces/Member.ts";
import SmartMultiSelect from "../../base/select/SmartMultiSelect.vue";
import {createCall, listAbortReasons, listCalls} from "../../../api/calls.ts";
import {emitCallCreated, emitError, emitSuccess} from "../../../events/bus.ts";
import {ADateTime} from "../../../scripts/datetime.ts";
import DateTimePicker from "../../base/datetime/DateTimePicker.vue";
import TimePicker from "../../base/datetime/TimePicker.vue";
import NumberPicker from "../../base/datetime/NumberPicker.vue";
import SmartSelect from "../../base/select/SmartSelect.vue";
import ConfirmButton from "../../base/buttons/derivates/ConfirmButton.vue";
import {t} from "../../../i18n";

const SUGGESTED_SUBJECTS = 8
const SUGGESTED_MEMBERS = 10

const subjects = ref<Subject[]>([])
const chosenSubjects = ref<Subject[]>([])
const members = ref<Member[]>([])
const abort_reasons = ref<String[]>([])
const selectedMembers = ref<Member[]>([])
const abort_reason = ref<string | null>(null)
const note = ref<string | null>(null)
const additional = ref<number>(0)
const start = ref<ADateTime>(ADateTime.now())
const end = ref<ADateTime>(ADateTime.now())
const submitting = ref(false)

const subjectSelect = ref<InstanceType<typeof SmartMultiSelect> | null>(null)
const memberSelect = ref<InstanceType<typeof SmartMultiSelect> | null>(null)
const reasonSelect = ref<InstanceType<typeof SmartSelect> | null>(null)
const startPicker = ref<InstanceType<typeof DateTimePicker> | null>(null)
const noteInput = ref<HTMLInputElement | null>(null)

const canSubmit = computed(() => chosenSubjects.value.length > 0 && selectedMembers.value.length > 0 && !submitting.value)

const duration = computed({
  get: () => {
    const minutes = (end.value.hour * 60 + end.value.minute) - (start.value.hour * 60 + start.value.minute)
    return minutes < 0 ? minutes + 24 * 60 : minutes
  },
  set: (minutes: number) => {
    end.value = start.value.addMinutes(minutes)
  }
})

onMounted(async () => {
  window.addEventListener('keydown', onHotkey)
  subjects.value = await listSubjects(false) as Subject[]
  members.value = await listMembers(true)
  abort_reasons.value = await listAbortReasons()
  subjectSelect.value?.focus()
})

onUnmounted(() => window.removeEventListener('keydown', onHotkey))

function onHotkey(e: KeyboardEvent) {
  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault()
    submit()
    return
  }
  if (!e.altKey || e.ctrlKey) return
  const targets: Record<string, () => void> = {
    s: () => subjectSelect.value?.focus(),
    z: () => startPicker.value?.focus(),
    m: () => memberSelect.value?.focus(),
    g: () => reasonSelect.value?.focus(),
    n: () => noteInput.value?.focus(),
    c: () => { void addLastCrew() }
  }
  const action = targets[e.key.toLowerCase()]
  if (action) {
    e.preventDefault()
    action()
  }
}

async function addLastCrew() {
  const page = await listCalls(1, 1)
  const last = page.entries[0]
  if (!last) {
    emitError(null, {message: t('calls.lastCrewEmpty')})
    return
  }
  const crew = members.value.filter(m => last.members.some(e => e.id === m.id))
  selectedMembers.value = [...selectedMembers.value,
    ...crew.filter(m => !selectedMembers.value.includes(m))]
}

async function submit() {
  if (!canSubmit.value) return
  submitting.value = true
  try {
    end.value = end.value.applyDate(start.value)
    if (start.value.toUnixTimestamp() > end.value.toUnixTimestamp()) {
      end.value = end.value.nextDay()
    }
    let call = {
      subjects: chosenSubjects.value.map(e => e.id!),
      start: start.value.toUnixTimestamp(),
      end: end.value.toUnixTimestamp(),
      additional: additional.value,
      members: selectedMembers.value.map(e => e.id!),
      note: note.value,
      abort_reason: abort_reason.value
    }

    await createCall(call)
    emitSuccess(t('calls.created'))
    emitCallCreated()
    chosenSubjects.value = []
    selectedMembers.value = []
    abort_reason.value = null
    note.value = null
    additional.value = 0
    start.value = ADateTime.now()
    end.value = ADateTime.now()
    subjectSelect.value?.focus()
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="card p-5 flex flex-col gap-4">
    <div class="flex items-baseline justify-between">
      <h2 class="headline text-xl">{{ t('calls.createTitle') }}</h2>
      <span class="label">{{ t('calls.shortcutHint') }}</span>
    </div>

    <div class="flex flex-col gap-2">
      <span class="label">{{ t('common.subject') }}</span>
      <SmartMultiSelect ref="subjectSelect" v-model="chosenSubjects" :options="subjects"
                        :value-mapper="(e:Subject) => e.name" :key-mapper="(e: Subject) => e.id!"
                        :weight-mapper="(e:Subject) => e.usage ?? 0" :hint-mapper="(e:Subject) => e.group"
                        :empty-limit="SUGGESTED_SUBJECTS"/>
    </div>

    <div class="flex flex-wrap items-end gap-6">
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('common.start') }}</span>
        <DateTimePicker ref="startPicker" v-model="start"/>
      </div>
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('common.end') }}</span>
        <TimePicker v-model="end"/>
      </div>
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('calls.duration') }}</span>
        <NumberPicker :max="1439" :min="0" v-model="duration"/>
      </div>
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('calls.followUp') }}</span>
        <NumberPicker :max="1000" :min="0" v-model="additional"/>
      </div>
    </div>

    <div class="flex flex-col gap-2">
      <div class="flex items-center justify-between">
        <span class="label">{{ t('common.members') }} · <span class="tabular text-ink">{{ selectedMembers.length }}</span></span>
        <button type="button" tabindex="-1" class="ghost-action" @click="addLastCrew">
          <font-awesome-icon icon="fa-solid fa-users"/>
          {{ t('calls.lastCrew') }}
        </button>
      </div>
      <SmartMultiSelect ref="memberSelect" v-model="selectedMembers" :options="members"
                        :value-mapper="(e:Member) => e.name" :key-mapper="(e:Member) => e.id"
                        :weight-mapper="(e:Member) => e.usage ?? 0" :empty-limit="SUGGESTED_MEMBERS"/>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('calls.abortReason') }}</span>
        <SmartSelect ref="reasonSelect" :key-mapper="(v) => v" :value-mapper="(k) => k as string"
                     :options="abort_reasons" :generator="(v:string) => v || null" v-model="abort_reason"/>
      </div>
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('common.note') }}</span>
        <input ref="noteInput" v-model="note" type="text" class="field"/>
      </div>
    </div>

    <div class="flex items-center gap-4 pt-1">
      <ConfirmButton :disabled="!canSubmit" @click="submit">{{ t('common.create') }}</ConfirmButton>
      <span class="tabular text-xs text-faint">{{ t('calls.shortcuts') }}</span>
    </div>
  </section>
</template>

<style scoped>
.ghost-action {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  height: 26px;
  padding: 0 10px;
  border: 1px solid var(--c-rule);
  border-radius: 3px;
  background: var(--c-surface);
  color: var(--c-ink);
  font-family: var(--font-condensed);
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
}

.ghost-action:hover {
  background: var(--c-raised);
}
</style>
