<script setup lang="ts">
import {useRoute} from "vue-router";
import {computed, onMounted, ref} from "vue";
import {getCall, removeCall, updateCall} from "../api/call.ts";
import type {FullCall} from "../interfaces/Call.ts";
import ErrorButton from "../components/base/buttons/derivates/ErrorButton.vue";
import StandardButton from "../components/base/buttons/StandardButton.vue";
import {RouterLink} from "vue-router";
import SimpleButton from "../components/base/buttons/SimpleButton.vue";
import router from "../router";
import {dayPosition, formatDate, formatDuration} from "../scripts/datetime.ts";
import {emitSuccess} from "../events/bus.ts";
import {isAdmin} from "../auth.ts";
import {t} from "../i18n";

const route = useRoute()

const id: number = Number(route.params.id!)
const call = ref<FullCall | null>(null)

const editingNote = ref(false)
const editingAbort = ref(false)
const editNote = ref('')
const editAbort = ref('')

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

function startEditNote() {
  editNote.value = call.value?.note ?? ''
  editingNote.value = true
}

async function saveNote() {
  if (!call.value) return
  await updateCall({
    id: call.value.id,
    start: call.value.start,
    end: call.value.end,
    additional: call.value.additional,
    note: editNote.value || null,
    abort_reason: call.value.abort_reason
  })
  call.value.note = editNote.value || null
  editingNote.value = false
  emitSuccess(t('calls.noteSaved'))
}

function startEditAbort() {
  editAbort.value = call.value?.abort_reason ?? ''
  editingAbort.value = true
}

async function saveAbort() {
  if (!call.value) return
  await updateCall({
    id: call.value.id,
    start: call.value.start,
    end: call.value.end,
    additional: call.value.additional,
    note: call.value.note,
    abort_reason: editAbort.value || null
  })
  call.value.abort_reason = editAbort.value || null
  editingAbort.value = false
  emitSuccess(t('calls.abortSaved'))
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

    <section class="card p-5 flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('calls.abortLabel') }}</span>
        <div v-if="!editingAbort" class="flex items-center gap-2">
          <span :class="call.abort_reason ? 'text-ink' : 'text-faint'">{{ call.abort_reason ?? '—' }}</span>
          <SimpleButton v-if="isAdmin()" @click="startEditAbort" :aria-label="t('common.edit')">
            <font-awesome-icon icon="fa-solid fa-pen"/>
          </SimpleButton>
        </div>
        <div v-else class="flex items-center gap-2">
          <input type="text" v-model="editAbort" class="field" style="max-width: 22rem"/>
          <SimpleButton @click="saveAbort" :aria-label="t('common.save')">
            <font-awesome-icon icon="fa-solid fa-check"/>
          </SimpleButton>
          <SimpleButton @click="editingAbort = false" :aria-label="t('common.cancel')">
            <font-awesome-icon icon="fa-solid fa-xmark"/>
          </SimpleButton>
        </div>
      </div>

      <div class="flex flex-col gap-2">
        <span class="label">{{ t('calls.note') }}</span>
        <div v-if="!editingNote" class="flex items-center gap-2">
          <span :class="call.note ? 'text-ink' : 'text-faint'">{{ call.note ?? '—' }}</span>
          <SimpleButton v-if="isAdmin()" @click="startEditNote" :aria-label="t('common.edit')">
            <font-awesome-icon icon="fa-solid fa-pen"/>
          </SimpleButton>
        </div>
        <div v-else class="flex items-center gap-2">
          <input type="text" v-model="editNote" class="field" style="max-width: 22rem"/>
          <SimpleButton @click="saveNote" :aria-label="t('common.save')">
            <font-awesome-icon icon="fa-solid fa-check"/>
          </SimpleButton>
          <SimpleButton @click="editingNote = false" :aria-label="t('common.cancel')">
            <font-awesome-icon icon="fa-solid fa-xmark"/>
          </SimpleButton>
        </div>
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
