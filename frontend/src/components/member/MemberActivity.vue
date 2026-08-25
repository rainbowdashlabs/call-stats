<script setup lang="ts">
import {computed, onMounted, type PropType, ref, watch} from "vue";
import VChart from "vue-echarts";
import {use} from "echarts/core";
import {CanvasRenderer} from "echarts/renderers";
import {BarChart, LineChart} from "echarts/charts";
import {GridComponent, LegendComponent, TitleComponent, ToolboxComponent, TooltipComponent} from "echarts/components";
import type {Member} from "../../interfaces/Member.ts";
import {
  getMemberCalls,
  getMemberYearSummary,
  getMemberYearTrend,
  getYearRange,
  type MemberCallEntry,
  type MemberYearSummary,
  type MemberYearTrendEntry
} from "../../api/statistics.ts";
import {formatDateTime} from "../../scripts/datetime.ts";
import router from "../../router";
import {t} from "../../i18n";
import {categoryAxis, chartBase, legend, screenTheme, title, tooltip, valueAxis} from "../../scripts/charts.ts";

use([CanvasRenderer, BarChart, LineChart, GridComponent, LegendComponent, TitleComponent, ToolboxComponent, TooltipComponent]);

const props = defineProps({
  member: {
    type: Object as PropType<Member>,
    required: true
  }
})

const theme = screenTheme
const YEARS_BACK = 5

const currentYear = new Date().getFullYear()
const selectedYear = ref(currentYear)
const years = ref<number[]>([currentYear])

const calls = ref<MemberCallEntry[]>([])
const stats = ref<MemberYearSummary | null>(null)
const trend = ref<MemberYearTrendEntry[]>([])
const loading = ref(false)

const thisYear = computed(() => trend.value.find(e => e.year === selectedYear.value) ?? null)

async function load() {
  loading.value = true
  try {
    const [entries, summary, history] = await Promise.all([
      getMemberCalls(props.member.id!, selectedYear.value),
      getMemberYearSummary(selectedYear.value, props.member.name),
      getMemberYearTrend(props.member.id!, selectedYear.value, YEARS_BACK)
    ])
    calls.value = entries
    stats.value = summary
    trend.value = history
  } finally {
    loading.value = false
  }
}

watch(selectedYear, () => load())

onMounted(async () => {
  const range = await getYearRange()
  const highest = Math.max(range.max_year, currentYear)
  years.value = Array.from({length: highest - range.min_year + 1}, (_, i) => highest - i)
  if (!years.value.includes(selectedYear.value)) selectedYear.value = highest
  await load()
})

const trendOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.memberTrend'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(trend.value.map(e => e.year), theme),
  yAxis: [valueAxis(t('statistics.charts.count'), theme), valueAxis('%', theme, {max: 100})],
  series: [
    {name: t('statistics.sections.calls'), type: 'bar', data: trend.value.map(e => e.call_count)},
    {name: t('statistics.sections.exercises'), type: 'bar', data: trend.value.map(e => e.exercise_count)},
    {name: t('statistics.sections.youth'), type: 'bar', data: trend.value.map(e => e.youth_count)},
    {name: t('statistics.charts.share'), type: 'line', yAxisIndex: 1, data: trend.value.map(e => e.call_count_perc)}
  ],
  legend: legend(theme, {top: 28}),
  grid: {left: '12%', right: '12%', top: 80}
}))
</script>

<template>
  <div class="mt-4">
    <div class="flex items-center gap-4 mb-2">
      <h2 class="text-xl font-bold">{{ t('members.activity.title') }}</h2>
      <select v-model="selectedYear" class="bg-gray-800 text-white px-2 py-1 rounded">
        <option v-for="y in years" :value="y">{{ y }}</option>
      </select>
    </div>

    <div v-if="stats" class="grid grid-cols-3 md:grid-cols-7 gap-2 mb-4">
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-orange-400">{{ stats.call_count }}</div>
        <div class="text-xs text-gray-400">{{ t('members.activity.calls') }}</div>
      </div>
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-green-400">{{ stats.call_hours }}h</div>
        <div class="text-xs text-gray-400">{{ t('members.activity.hours') }}</div>
      </div>
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-blue-400">{{ stats.call_count_perc }}%</div>
        <div class="text-xs text-gray-400">{{ t('members.activity.shareCalls') }}</div>
      </div>
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-purple-400">{{ stats.call_hours_perc }}%</div>
        <div class="text-xs text-gray-400">{{ t('members.activity.shareHours') }}</div>
      </div>
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-yellow-400">{{ stats.rank }} / {{ stats.member_count }}</div>
        <div class="text-xs text-gray-400">{{ t('members.activity.rank') }}</div>
      </div>
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-cyan-400">{{ thisYear?.exercise_count ?? 0 }}</div>
        <div class="text-xs text-gray-400">{{ t('statistics.sections.exercises') }}</div>
      </div>
      <div class="bg-gray-800 rounded p-2 text-center">
        <div class="text-xl font-bold text-teal-400">{{ thisYear?.youth_count ?? 0 }}</div>
        <div class="text-xs text-gray-400">{{ t('statistics.sections.youth') }}</div>
      </div>
    </div>

    <div v-if="trend.length" class="bg-gray-900 rounded-lg p-2 mb-4">
      <VChart :option="trendOption" style="height: 280px;" autoresize/>
    </div>

    <div v-if="loading" class="p-2">{{ t('common.loading') }}</div>
    <div v-else-if="calls.length === 0" class="p-2 text-gray-400">{{ t('members.activity.empty', { year: selectedYear }) }}</div>
    <div v-else class="border border-gray-700 rounded-lg overflow-hidden">
      <div class="grid grid-cols-3 gap-2 p-2 font-bold bg-gray-800">
        <div>{{ t('common.subject') }}</div>
        <div>{{ t('common.start') }}</div>
        <div>{{ t('common.end') }}</div>
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
