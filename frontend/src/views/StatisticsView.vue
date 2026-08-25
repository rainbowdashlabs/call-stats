<script setup lang="ts">
import {computed, onMounted, ref, watch} from "vue";
import VChart from "vue-echarts";
import {use} from "echarts/core";
import {CanvasRenderer} from "echarts/renderers";
import {LineChart, BarChart, PieChart} from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent
} from "echarts/components";
import {
  getDailyCalls,
  getMemberDailyCalls,
  getCallGroups,
  getCallGroupsMonthly,
  getYearSummary,
  getMemberYearStats,
  type DailyCallCount,
  type MemberDailyStats,
  type CallGroupCount,
  type CallGroupMonthCount,
  type YearSummary,
  type MemberYearStats
} from "../api/statistics.ts";
import {listMembers} from "../api/members.ts";
import type {Member} from "../interfaces/Member.ts";

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent
]);

// Filters
const currentYear = new Date().getFullYear()
const selectedYear = ref(currentYear)
const rollingDays = ref(30)
const selectedMember = ref<string>('')
const years = Array.from({length: 10}, (_, i) => currentYear - i)

// Data
const members = ref<Member[]>([])
const dailyCalls = ref<DailyCallCount[]>([])
const memberDailyCalls = ref<MemberDailyStats[]>([])
const callGroups = ref<CallGroupCount[]>([])
const callGroupsMonthly = ref<CallGroupMonthCount[]>([])
const yearSummary = ref<YearSummary | null>(null)
const memberYearStats = ref<MemberYearStats[]>([])
const loading = ref(false)

// Date range filter
const startDate = ref('')
const endDate = ref('')

async function loadMembers() {
  members.value = await listMembers(false)
}

async function loadStats() {
  loading.value = true
  try {
    const [dc, cg, cgm, ys, mys] = await Promise.all([
      getDailyCalls(selectedYear.value, rollingDays.value),
      getCallGroups(selectedYear.value),
      getCallGroupsMonthly(selectedYear.value),
      getYearSummary(selectedYear.value),
      getMemberYearStats(selectedYear.value)
    ])
    dailyCalls.value = dc
    callGroups.value = cg
    callGroupsMonthly.value = cgm
    yearSummary.value = ys
    memberYearStats.value = mys

    if (selectedMember.value) {
      memberDailyCalls.value = await getMemberDailyCalls(selectedYear.value, rollingDays.value, selectedMember.value)
    } else {
      memberDailyCalls.value = []
    }
  } finally {
    loading.value = false
  }
}

async function loadMemberStats() {
  if (selectedMember.value) {
    memberDailyCalls.value = await getMemberDailyCalls(selectedYear.value, rollingDays.value, selectedMember.value)
  } else {
    memberDailyCalls.value = []
  }
}

watch([selectedYear, rollingDays], () => loadStats())
watch(selectedMember, () => loadMemberStats())

onMounted(async () => {
  await loadMembers()
  await loadStats()
})

// Filtered daily calls by date range
const filteredDailyCalls = computed(() => {
  let data = dailyCalls.value
  if (startDate.value) data = data.filter(d => d.day >= startDate.value)
  if (endDate.value) data = data.filter(d => d.day <= endDate.value)
  return data
})

const filteredMemberDailyCalls = computed(() => {
  let data = memberDailyCalls.value
  if (startDate.value) data = data.filter(d => d.day >= startDate.value)
  if (endDate.value) data = data.filter(d => d.day <= endDate.value)
  return data
})

// Chart options
const dailyCallsChartOption = computed(() => ({
  title: {text: `Einsaetze (${rollingDays.value}-Tage rollierend)`, textStyle: {color: '#fff'}},
  tooltip: {trigger: 'axis'},
  xAxis: {type: 'category', data: filteredDailyCalls.value.map(d => d.day), axisLabel: {color: '#ccc'}},
  yAxis: [
    {type: 'value', name: 'Anzahl', axisLabel: {color: '#ccc'}, nameTextStyle: {color: '#ccc'}},
    {type: 'value', name: 'Stunden', axisLabel: {color: '#ccc'}, nameTextStyle: {color: '#ccc'}}
  ],
  series: [
    {name: 'Einsaetze', type: 'line', data: filteredDailyCalls.value.map(d => d.call_count), smooth: true, itemStyle: {color: '#f97316'}},
    {name: 'Stunden', type: 'line', yAxisIndex: 1, data: filteredDailyCalls.value.map(d => d.call_hours), smooth: true, itemStyle: {color: '#22c55e'}}
  ],
  legend: {textStyle: {color: '#ccc'}},
  grid: {left: '10%', right: '10%'},
  dataZoom: [{type: 'inside'}, {type: 'slider'}],
  backgroundColor: 'transparent'
}))

const memberDailyChartOption = computed(() => {
  if (!filteredMemberDailyCalls.value.length) return null
  return {
    title: {text: `${selectedMember.value} - Einsaetze (${rollingDays.value}-Tage rollierend)`, textStyle: {color: '#fff'}},
    tooltip: {trigger: 'axis'},
    xAxis: {type: 'category', data: filteredMemberDailyCalls.value.map(d => d.day), axisLabel: {color: '#ccc'}},
    yAxis: [
      {type: 'value', name: 'Anzahl', axisLabel: {color: '#ccc'}, nameTextStyle: {color: '#ccc'}},
      {type: 'value', name: '%', max: 100, axisLabel: {color: '#ccc'}, nameTextStyle: {color: '#ccc'}}
    ],
    series: [
      {name: 'Eigene Einsaetze', type: 'line', data: filteredMemberDailyCalls.value.map(d => d.call_count), smooth: true, itemStyle: {color: '#f97316'}},
      {name: 'Gesamt Einsaetze', type: 'line', data: filteredMemberDailyCalls.value.map(d => d.call_count_total), smooth: true, itemStyle: {color: '#666'}},
      {name: 'Anteil %', type: 'line', yAxisIndex: 1, data: filteredMemberDailyCalls.value.map(d => d.call_count_percentage), smooth: true, itemStyle: {color: '#22c55e'}}
    ],
    legend: {textStyle: {color: '#ccc'}},
    grid: {left: '10%', right: '10%'},
    dataZoom: [{type: 'inside'}, {type: 'slider'}],
    backgroundColor: 'transparent'
  }
})

const callGroupsPieOption = computed(() => ({
  title: {text: 'Einsaetze nach Gruppe', textStyle: {color: '#fff'}},
  tooltip: {trigger: 'item'},
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: callGroups.value.map(g => ({name: g.group, value: g.call_count})),
    label: {color: '#ccc'}
  }],
  legend: {orient: 'vertical', right: 10, top: 'center', textStyle: {color: '#ccc'}},
  backgroundColor: 'transparent'
}))

const monthlyGroupsChartOption = computed(() => {
  const groups = [...new Set(callGroupsMonthly.value.map(d => d.group))]
  const months = [...new Set(callGroupsMonthly.value.map(d => d.month))].sort()

  return {
    title: {text: 'Einsaetze pro Monat nach Gruppe', textStyle: {color: '#fff'}},
    tooltip: {trigger: 'axis'},
    xAxis: {type: 'category', data: months.map(m => m.substring(0, 7)), axisLabel: {color: '#ccc'}},
    yAxis: {type: 'value', axisLabel: {color: '#ccc'}},
    series: groups.map(group => ({
      name: group,
      type: 'bar',
      stack: 'total',
      data: months.map(m => {
        const entry = callGroupsMonthly.value.find(d => d.month === m && d.group === group)
        return entry?.call_count ?? 0
      })
    })),
    legend: {textStyle: {color: '#ccc'}},
    grid: {left: '10%', right: '5%'},
    backgroundColor: 'transparent'
  }
})

const memberRankingChartOption = computed(() => {
  const sorted = [...memberYearStats.value].sort((a, b) => b.call_count - a.call_count)
  return {
    title: {text: 'Mitglieder Ranking', textStyle: {color: '#fff'}},
    tooltip: {trigger: 'axis'},
    xAxis: {type: 'category', data: sorted.map(m => m.member_name), axisLabel: {color: '#ccc', rotate: 45}},
    yAxis: [
      {type: 'value', name: 'Einsaetze', axisLabel: {color: '#ccc'}, nameTextStyle: {color: '#ccc'}},
      {type: 'value', name: 'Stunden', axisLabel: {color: '#ccc'}, nameTextStyle: {color: '#ccc'}}
    ],
    series: [
      {name: 'Einsaetze', type: 'bar', data: sorted.map(m => m.call_count), itemStyle: {color: '#f97316'}},
      {name: 'Stunden', type: 'bar', yAxisIndex: 1, data: sorted.map(m => m.call_hours), itemStyle: {color: '#22c55e'}}
    ],
    legend: {textStyle: {color: '#ccc'}},
    grid: {left: '10%', right: '10%', bottom: '20%'},
    dataZoom: [{type: 'inside'}, {type: 'slider'}],
    backgroundColor: 'transparent'
  }
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-2xl">Statistiken</h1>

    <!-- Filters -->
    <div class="flex flex-wrap gap-4 items-end p-4 border border-gray-700 rounded-lg">
      <div>
        <label class="block text-sm text-gray-400">Jahr</label>
        <select v-model="selectedYear" class="bg-gray-800 text-white px-3 py-2 rounded">
          <option v-for="y in years" :value="y">{{ y }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm text-gray-400">Rollierende Tage</label>
        <select v-model="rollingDays" class="bg-gray-800 text-white px-3 py-2 rounded">
          <option v-for="d in [7, 14, 30, 60, 90, 180, 365]" :value="d">{{ d }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm text-gray-400">Von</label>
        <input type="date" v-model="startDate" class="bg-gray-800 text-white px-3 py-2 rounded"/>
      </div>
      <div>
        <label class="block text-sm text-gray-400">Bis</label>
        <input type="date" v-model="endDate" class="bg-gray-800 text-white px-3 py-2 rounded"/>
      </div>
      <div>
        <label class="block text-sm text-gray-400">Mitglied</label>
        <select v-model="selectedMember" class="bg-gray-800 text-white px-3 py-2 rounded">
          <option value="">-- Alle --</option>
          <option v-for="m in members" :value="m.name">{{ m.name }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="text-center p-8">Laden...</div>

    <template v-else>
      <!-- Year Summary -->
      <div v-if="yearSummary" class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-orange-400">{{ yearSummary.call_count }}</div>
          <div class="text-sm text-gray-400">Einsaetze</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-red-400">{{ yearSummary.aborted }}</div>
          <div class="text-sm text-gray-400">Abgebrochen</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-green-400">{{ yearSummary.count_call_hours }}</div>
          <div class="text-sm text-gray-400">Einsatzstunden</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-blue-400">{{ yearSummary.count_crew_hours }}</div>
          <div class="text-sm text-gray-400">Mannschaftsstunden</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-purple-400">{{ yearSummary.half_hours_members ?? '-' }}%</div>
          <div class="text-sm text-gray-400">50%-Anteil</div>
        </div>
      </div>

      <!-- Daily Calls Chart -->
      <div class="bg-gray-900 rounded-lg p-4">
        <VChart :option="dailyCallsChartOption" style="height: 350px;" autoresize/>
      </div>

      <!-- Member Daily Chart (if member selected) -->
      <div v-if="memberDailyChartOption" class="bg-gray-900 rounded-lg p-4">
        <VChart :option="memberDailyChartOption" style="height: 350px;" autoresize/>
      </div>

      <!-- Call Groups and Monthly -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="callGroupsPieOption" style="height: 350px;" autoresize/>
        </div>
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="monthlyGroupsChartOption" style="height: 350px;" autoresize/>
        </div>
      </div>

      <!-- Member Ranking -->
      <div class="bg-gray-900 rounded-lg p-4">
        <VChart :option="memberRankingChartOption" style="height: 400px;" autoresize/>
      </div>
    </template>
  </div>
</template>
