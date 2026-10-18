<script setup lang="ts">
import {useRoute} from "vue-router";
import {computed, onMounted, ref} from "vue";
import {getCall, removeCall, updateCall} from "../api/call.ts";
import {listSubjects} from "../api/subjects.ts";
import {listMembers} from "../api/members.ts";
import {listAbortReasons} from "../api/calls.ts";
import type {FullCall} from "../interfaces/Call.ts";
import type {Subject} from "../interfaces/Subject.ts";
import type {Member} from "../interfaces/Member.ts";
import ErrorButton from "../components/base/buttons/derivates/ErrorButton.vue";
import ConfirmButton from "../components/base/buttons/derivates/ConfirmButton.vue";
import StandardButton from "../components/base/buttons/StandardButton.vue";
import {RouterLink} from "vue-router";
import SmartMultiSelect from "../components/base/select/SmartMultiSelect.vue";
import SmartSelect from "../components/base/select/SmartSelect.vue";
import DateTimePicker from "../components/base/datetime/DateTimePicker.vue";
import TimePicker from "../components/base/datetime/TimePicker.vue";
import NumberPicker from "../components/base/datetime/NumberPicker.vue";
import router from "../router";
import {ADateTime, dayPosition, formatDate, formatDuration} from "../scripts/datetime.ts";
import {emitSuccess} from "../events/bus.ts";
import {isAdmin} from "../auth.ts";
import {t} from "../i18n";

const route = useRoute()

const id: number = Number(route.params.id!)
const call = ref<FullCall | null>(null)

const editing = ref(false)
const saving = ref(false)
const subjectOptions = ref<Subject[]>([])
const memberOptions = ref<Member[]>([])
const abortReasons = ref<String[]>([])
const editSubjects = ref<Subject[]>([])
const editMembers = ref<Member[]>([])
const editStart = ref<ADateTime>(ADateTime.now())
const editEnd = ref<ADateTime>(ADateTime.now())
const editAdditional = ref(0)
const editAbort = ref<string | null>(null)
const editNote = ref<string | null>(null)

async function load() {
  call.value = await getCall(id)
}

const confirmDelete = ref(false)

async function remove() {
  if (!confirmDelete.value) {
    confirmDelete.value = true
    return
  }
  await removeCall(id)
  await router.push({name: "Calls"})
}

const canSave = computed(() => editSubjects.value.length > 0 && editMembers.value.length > 0 && !saving.value)

const editDuration = computed({
  get: () => {
    const minutes = (editEnd.value.hour * 60 + editEnd.value.minute) - (editStart.value.hour * 60 + editStart.value.minute)
    return minutes < 0 ? minutes + 24 * 60 : minutes
  },
  set: (minutes: number) => {
    editEnd.value = editStart.value.addMinutes(minutes)
  }
})

/** Picks the option object for each stored item so the selects can tell chosen from available. */
function pickOptions<T extends {id?: number}>(options: T[], stored: T[]): T[] {
  const chosen: T[] = []
  for (const item of stored) {
    let option = options.find(o => o.id === item.id)
    if (!option) {
      option = item
      options.push(item)
    }
    chosen.push(option)
  }
  return chosen
}

async function startEdit() {
  if (!call.value) return
  const start = ADateTime.fromDate(new Date(call.value.start as string))
  const [subjects, members, reasons] = await Promise.all([
    listSubjects(false) as Promise<Subject[]>,
    listMembers(true, start.toUnixTimestamp()),
    listAbortReasons()
  ])
  subjectOptions.value = subjects
  memberOptions.value = members
  abortReasons.value = reasons
  editSubjects.value = pickOptions(subjectOptions.value, call.value.subjects as Subject[])
  editMembers.value = pickOptions(memberOptions.value, call.value.members as Member[])
  editStart.value = start
  editEnd.value = ADateTime.fromDate(new Date(call.value.end as string))
  editAdditional.value = call.value.additional
  editAbort.value = call.value.abort_reason ?? null
  editNote.value = call.value.note ?? null
  editing.value = true
}

async function save() {
  if (!call.value || !canSave.value) return
  saving.value = true
  try {
    let end = editEnd.value.applyDate(editStart.value)
    if (editStart.value.toUnixTimestamp() > end.toUnixTimestamp()) {
      end = end.nextDay()
    }
    call.value = await updateCall({
      id: call.value.id,
      subjects: editSubjects.value.map(e => e.id!),
      start: editStart.value.toUnixTimestamp(),
      end: end.toUnixTimestamp(),
      additional: editAdditional.value,
      members: editMembers.value.map(e => e.id!),
      note: editNote.value || null,
      abort_reason: editAbort.value || null
    })
    editing.value = false
    emitSuccess(t('calls.saved'))
  } finally {
    saving.value = false
  }
}

const subjects = computed(() => {
  return call.value?.subjects.map(v => v.name).join(" + ")
})

function clock(value: string | number | undefined): string {
  if (!value) return ""
  const date = new Date(value as string)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const band = computed(() => call.value ? dayPosition(call.value.start, call.value.end) : {left: 0, width: 0})

const minutes = computed(() => call.value
    ? (new Date(call.value.end as string).getTime() - new Date(call.value.start as string).getTime()) / 60000
    : 0)

const crewHours = computed(() => Math.round(minutes.value * (call.value?.members.length ?? 0) / 60))

onMounted(load)
</script>

<template>
  <article v-if="call" class="flex flex-col gap-5">
    <header class="flex items-start justify-between gap-6">
      <div class="min-w-0">
        <div class="eyebrow">{{ formatDate(call.start as string) }}</div>
        <h1 class="headline text-4xl mt-1">{{ subjects }}</h1>
        <div class="flex flex-wrap gap-2 mt-3">
          <span v-for="subject in call.subjects" :key="subject.id" class="tag">{{ subject.group }}</span>
          <span v-if="call.abort_reason" class="tag tag-signal">{{ t('calls.aborted') }}</span>
        </div>
      </div>
      <div v-if="isAdmin()" class="flex gap-2 shrink-0">
        <StandardButton v-if="!editing" @click="startEdit">
          <font-awesome-icon icon="fa-solid fa-pen"/>
          {{ t('common.edit') }}
        </StandardButton>
        <StandardButton v-if="confirmDelete" @click="confirmDelete = false">{{ t('common.cancel') }}</StandardButton>
        <ErrorButton @click="remove">
          <font-awesome-icon icon="fa-solid fa-trash"/>
          {{ confirmDelete ? t('common.deleteConfirm') : t('common.delete') }}
        </ErrorButton>
      </div>
    </header>

    <section class="card p-5">
      <div class="flex items-baseline justify-between">
        <span class="label">{{ t('calls.band') }}</span>
        <span class="tabular text-sm">{{ clock(call.start) }} – {{ clock(call.end) }}</span>
      </div>
      <div class="band mt-3">
        <div class="band-bar" :class="{aborted: !!call.abort_reason}"
             :style="{left: band.left + '%', width: band.width + '%'}"></div>
      </div>
      <div class="flex justify-between mt-2">
        <span v-for="hour in [0, 6, 12, 18, 24]" :key="hour" class="tabular text-[11px] text-faint">{{ hour }}</span>
      </div>
    </section>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-4">
        <div class="headline text-3xl tabular">{{ formatDuration(minutes) }}</div>
        <div class="label mt-1">{{ t('common.duration') }}</div>
      </div>
      <div class="card p-4">
        <div class="headline text-3xl tabular">{{ call.members.length }}</div>
        <div class="label mt-1">{{ t('calls.strength') }}</div>
      </div>
      <div class="card p-4">
        <div class="headline text-3xl tabular">{{ crewHours }}</div>
        <div class="label mt-1">{{ t('statistics.summary.crewHours') }}</div>
      </div>
      <div class="card p-4">
        <div class="headline text-3xl tabular">{{ call.additional }}</div>
        <div class="label mt-1">{{ t('calls.followUp') }}</div>
      </div>
    </div>

    <section v-if="editing" class="card p-5 flex flex-col gap-4">
      <h2 class="headline text-xl">{{ t('calls.editTitle') }}</h2>

      <div class="flex flex-col gap-2">
        <span class="label">{{ t('common.subject') }}</span>
        <SmartMultiSelect v-model="editSubjects" :options="subjectOptions"
                          :value-mapper="(e:Subject) => e.name" :key-mapper="(e: Subject) => e.id!"
                          :weight-mapper="(e:Subject) => e.usage ?? 0" :hint-mapper="(e:Subject) => e.group"/>
      </div>

      <div class="flex flex-wrap items-end gap-6">
        <div class="flex flex-col gap-2">
          <span class="label">{{ t('common.start') }}</span>
          <DateTimePicker v-model="editStart"/>
        </div>
        <div class="flex flex-col gap-2">
          <span class="label">{{ t('common.end') }}</span>
          <TimePicker v-model="editEnd"/>
        </div>
        <div class="flex flex-col gap-2">
          <span class="label">{{ t('calls.duration') }}</span>
          <NumberPicker :max="1439" :min="0" v-model="editDuration"/>
        </div>
        <div class="flex flex-col gap-2">
          <span class="label">{{ t('calls.followUp') }}</span>
          <NumberPicker :max="1000" :min="0" v-model="editAdditional"/>
        </div>
      </div>

      <div class="flex flex-col gap-2">
        <span class="label">{{ t('common.members') }} · <span class="tabular text-ink">{{ editMembers.length }}</span></span>
        <SmartMultiSelect v-model="editMembers" :options="memberOptions"
                          :value-mapper="(e:Member) => e.name" :key-mapper="(e:Member) => e.id"
                          :weight-mapper="(e:Member) => e.usage ?? 0"/>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex flex-col gap-2">
          <span class="label">{{ t('calls.abortReason') }}</span>
          <SmartSelect :key-mapper="(v) => v" :value-mapper="(k) => k as string"
                       :options="abortReasons" :generator="(v:string) => v || null" v-model="editAbort"/>
        </div>
        <div class="flex flex-col gap-2">
          <span class="label">{{ t('common.note') }}</span>
          <input v-model="editNote" type="text" class="field"/>
        </div>
      </div>

      <div class="flex items-center gap-2 pt-1">
        <ConfirmButton :disabled="!canSave" @click="save">{{ t('common.save') }}</ConfirmButton>
        <StandardButton @click="editing = false">{{ t('common.cancel') }}</StandardButton>
      </div>
    </section>

    <section v-else class="card p-5 flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('calls.abortLabel') }}</span>
        <span :class="call.abort_reason ? 'text-ink' : 'text-faint'">{{ call.abort_reason ?? '—' }}</span>
      </div>

      <div class="flex flex-col gap-2">
        <span class="label">{{ t('calls.note') }}</span>
        <span :class="call.note ? 'text-ink' : 'text-faint'">{{ call.note ?? '—' }}</span>
      </div>
    </section>

    <section class="card p-5">
      <div class="flex items-baseline justify-between">
        <span class="label">{{ t('common.members') }}</span>
        <span class="tabular text-sm text-muted">{{ call.members.length }}</span>
      </div>
      <div class="flex flex-wrap gap-2 mt-3">
        <RouterLink v-for="member in call.members" :key="member.id" class="tag tag-link"
                    :to="{name: 'Member', params: {id: member.id}}">{{ member.name }}</RouterLink>
      </div>
    </section>
  </article>

  <div v-else class="p-10 text-center text-muted">{{ t('common.loading') }}</div>
</template>

<style scoped>
.tag {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 10px;
  border: 1px solid var(--c-rule);
  border-radius: 3px;
  background: var(--c-raised);
  font-family: var(--font-condensed);
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--c-muted);
}

.tag-signal {
  border-color: var(--c-signal);
  background: var(--c-signal-soft);
  color: var(--c-signal-ink);
}

.tag-link {
  font-family: var(--font-sans);
  font-weight: 500;
  font-size: 14px;
  letter-spacing: 0;
  text-transform: none;
  color: var(--c-ink);
}

.tag-link:hover {
  border-color: var(--c-ink);
  color: var(--c-ink);
}

.band {
  position: relative;
  height: 14px;
  background: var(--c-band-track);
  border-radius: 2px;
}

.band-bar {
  position: absolute;
  top: 0;
  bottom: 0;
  min-width: 3px;
  background: var(--c-band);
  border-radius: 2px;
}

.band-bar.aborted {
  background: var(--c-signal);
}
</style>
