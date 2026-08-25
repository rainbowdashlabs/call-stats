<script setup lang="ts">
import {onMounted, type PropType, ref, watch} from "vue";
import type {Member} from "../../interfaces/Member.ts";
import {getMemberCalls, getMemberYearStats, type MemberCallEntry, type MemberYearStats} from "../../api/statistics.ts";
import {formatDateTime} from "../../scripts/datetime.ts";
import router from "../../router";

const props = defineProps({
  member: {
    type: Object as PropType<Member>,
    required: true
  }
})

const currentYear = new Date().getFullYear()
const selectedYear = ref(currentYear)
const years = Array.from({length: 10}, (_, i) => currentYear - i)

const calls = ref<MemberCallEntry[]>([])
const stats = ref<MemberYearStats | null>(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    calls.value = await getMemberCalls(props.member.id!, selectedYear.value)
    const allStats = await getMemberYearStats(selectedYear.value)
    stats.value = allStats.find(s => s.member_name === props.member.name) ?? null
  } finally {
    loading.value = false
  }
}

watch(selectedYear, () => load())
onMounted(load)
</script>

<template>
  <div class="mt-4">
    <div class="flex items-center gap-4 mb-2">
      <h2 class="text-xl font-bold">Einsatz-Historie</h2>
      <select v-model="selectedYear" class="bg-gray-800 text-white px-2 py-1 rounded">
        <option v-for="y in years" :value="y">{{ y }}</option>
      </select>
    </div>

    <!-- Stats summary -->
    <div v-if="stats" class="grid grid-cols-4 gap-2 mb-4">
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-orange-400">{{ stats.call_count }}</div>
        <div class="text-xs text-gray-400">Einsaetze</div>
      </div>
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-green-400">{{ stats.call_hours }}h</div>
        <div class="text-xs text-gray-400">Stunden</div>
      </div>
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-blue-400">{{ stats.call_count_perc }}%</div>
        <div class="text-xs text-gray-400">Anteil Einsaetze</div>
      </div>
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-purple-400">{{ stats.call_hours_perc }}%</div>
        <div class="text-xs text-gray-400">Anteil Stunden</div>
      </div>
    </div>

    <div v-if="loading" class="p-2">Laden...</div>
    <div v-else-if="calls.length === 0" class="p-2 text-gray-400">Keine Einsaetze in {{ selectedYear }}.</div>
    <div v-else class="border border-gray-700 rounded-lg overflow-hidden">
      <div class="grid grid-cols-3 gap-2 p-2 font-bold bg-gray-800">
        <div>Stichwort</div>
        <div>Start</div>
        <div>Ende</div>
      </div>
      <div v-for="call in calls" :key="call.call_id"
           class="grid grid-cols-3 gap-2 p-2 hover:bg-gray-800 cursor-pointer border-t border-gray-700"
           @click="router.push({name: 'Call', params: {id: call.call_id}})">
        <div>{{ call.subjects }}</div>
        <div>{{ formatDateTime(call.start) }}</div>
        <div>{{ formatDateTime(call.end) }}</div>
      </div>
    </div>
  </div>
</template>
