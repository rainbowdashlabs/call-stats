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
  getMemberDailyCalls,
  getCallTimeProfile,
  type MemberCallEntry,
  type MemberYearSummary,
  type MemberYearTrendEntry,
  type MemberDailyStats,
  type CallTimeProfileEntry
} from "../../api/statistics.ts";
import {formatDateTime} from "../../scripts/datetime.ts";
import router from "../../router";
import {t} from "../../i18n";
import {categoryAxis, chartBase, legend, screenTheme, title, tooltip, valueAxis, zoom} from "../../scripts/charts.ts";
import {DataZoomComponent} from "echarts/components";

use([CanvasRenderer, BarChart, LineChart, GridComponent, LegendComponent, TitleComponent, ToolboxComponent,
  TooltipComponent, DataZoomComponent]);

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
const rolling = ref<MemberDailyStats[]>([])
const timeProfile = ref<CallTimeProfileEntry[]>([])
const rollingDays = ref(30)
const loading = ref(false)

const thisYear = computed(() => trend.value.find(e => e.year === selectedYear.value) ?? null)

async function load() {
  loading.value = true
  try {
    const [entries, summary, history, daily, profile] = await Promise.all([
      getMemberCalls(props.member.id!, selectedYear.value),
      getMemberYearSummary(selectedYear.value, props.member.name),
      getMemberYearTrend(props.member.id!, selectedYear.value, YEARS_BACK),
      getMemberDailyCalls(selectedYear.value, rollingDays.value, props.member.name),
      getCallTimeProfile(selectedYear.value)
    ])
    calls.value = entries
    stats.value = summary
    trend.value = history
    rolling.value = daily
    timeProfile.value = profile
  } finally {
    loading.value = false
  }
}

watch([selectedYear, rollingDays], () => load())

onMounted(async () => {
  const range = await getYearRange()
  const highest = Math.max(range.max_year, currentYear)
  years.value = Array.from({length: highest - range.min_year + 1}, (_, i) => highest - i)
  if (!years.value.includes(selectedYear.value)) selectedYear.value = highest
  await load()
})

/** Eigene Alarme gegen die der ganzen Wehr, rollierend (Grafana 30/31/32). */
const rollingOption = computed(() => {
  if (!rolling.value.length) return null
  const days = rolling.value.map(d => d.day)
  return {
    ...chartBase(theme),
    title: title(t('members.activity.rolling', {days: rollingDays.value}), theme),
    tooltip: tooltip(theme),
    xAxis: categoryAxis(days, theme),
    yAxis: [valueAxis(t('statistics.charts.count'), theme), valueAxis('%', theme, {max: 100})],
    series: [
      {name: t('statistics.charts.ownCalls'), type: 'line', smooth: true, showSymbol: false,
        data: rolling.value.map(d => d.call_count)},
      {name: t('statistics.charts.totalCalls'), type: 'line', smooth: true, showSymbol: false,
        lineStyle: {type: 'dashed'}, itemStyle: {color: '#f87171'}, data: rolling.value.map(d => d.call_count_total)},
      {name: t('statistics.charts.hours'), type: 'line', smooth: true, showSymbol: false,
        data: rolling.value.map(d => d.call_hours)},
      {name: t('statistics.charts.percentCalls'), type: 'line', yAxisIndex: 1, smooth: true, showSymbol: false,
        data: rolling.value.map(d => d.call_count_percentage)},
      {name: t('statistics.charts.percentHours'), type: 'line', yAxisIndex: 1, smooth: true, showSymbol: false,
        data: rolling.value.map(d => d.call_hours_percentage)}
    ],
    legend: legend(theme, {top: 28, type: 'scroll'}),
    grid: {left: '12%', right: '12%', top: 90},
    dataZoom: zoom(theme)
  }
})

/**
 * Zu welcher Tageszeit die eigenen Alarme liegen und welcher Anteil der Alarme dieser Stunde das
 * ist (Grafana 28). Die Gesamtzahl je Stunde kommt aus dem Wochenprofil aller Einsätze.
 */
const hourProfileOption = computed(() => {
  if (!calls.value.length) return null
  const own = new Array(24).fill(0)
  for (const call of calls.value) own[new Date(call.start).getHours()]++
  const total = new Array(24).fill(0)
  for (const entry of timeProfile.value) total[entry.hour] += entry.call_count
  const share = own.map((count, hour) => total[hour] ? Math.round(count * 100 / total[hour]) : 0)
  return {
    ...chartBase(theme),
    title: title(t('members.activity.hourProfile'), theme),
    tooltip: tooltip(theme),
    xAxis: categoryAxis(Array.from({length: 24}, (_, h) => `${String(h).padStart(2, '0')}:00`), theme),
    yAxis: [valueAxis(t('statistics.charts.count'), theme), valueAxis('%', theme, {max: 100})],
    series: [
      {name: t('members.activity.calls'), type: 'bar', data: own, itemStyle: {color: '#facc15'}},
      {name: t('statistics.charts.totalCalls'), type: 'bar', data: total, itemStyle: {color: '#475569'}},
      {name: t('statistics.charts.share'), type: 'line', yAxisIndex: 1, data: share}
    ],
    legend: legend(theme, {top: 28}),
    grid: {left: '12%', right: '12%', top: 90}
  }
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
      <h2 class="headline text-2xl tabular">{{ t('members.activity.title') }}</h2>
      <select v-model="selectedYear" class="bg-surface text-white px-2 py-1 rounded">
        <option v-for="y in years" :value="y">{{ y }}</option>
      </select>
    </div>

    <div v-if="stats" class="grid grid-cols-3 md:grid-cols-7 gap-2 mb-4">
      <div class="card p-3 text-center">
        <div class="headline text-2xl tabular text-ink">{{ stats.call_count }}</div>
        <div class="label mt-1">{{ t('members.activity.calls') }}</div>
      </div>
      <div class="card p-3 text-center">
        <div class="headline text-2xl tabular text-ink">{{ stats.call_hours }}h</div>
        <div class="label mt-1">{{ t('members.activity.hours') }}</div>
      </div>
      <div class="card p-3 text-center">
        <div class="headline text-2xl tabular text-ink">{{ stats.call_count_perc }}%</div>
        <div class="label mt-1">{{ t('members.activity.shareCalls') }}</div>
      </div>
      <div class="card p-3 text-center">
        <div class="headline text-2xl tabular text-ink">{{ stats.call_hours_perc }}%</div>
        <div class="label mt-1">{{ t('members.activity.shareHours') }}</div>
      </div>
      <div class="card p-3 text-center">
        <div class="headline text-2xl tabular text-ink">{{ stats.rank }} / {{ stats.member_count }}</div>
        <div class="label mt-1">{{ t('members.activity.rank') }}</div>
      </div>
      <div class="card p-3 text-center">
        <div class="headline text-2xl tabular text-ink">{{ thisYear?.exercise_count ?? 0 }}</div>
        <div class="label mt-1">{{ t('statistics.sections.exercises') }}</div>
      </div>
      <div class="card p-3 text-center">
        <div class="headline text-2xl tabular text-ink">{{ thisYear?.youth_count ?? 0 }}</div>
        <div class="label mt-1">{{ t('statistics.sections.youth') }}</div>
      </div>
    </div>

    <div v-if="trend.length" class="card p-3 mb-4">
      <VChart :option="trendOption" style="height: 280px;" autoresize/>
    </div>

    <div v-if="rollingOption" class="card p-3 mb-4">
      <div class="flex justify-end items-center gap-2 text-sm text-muted">
        <label>{{ t('statistics.rollingDays') }}</label>
        <select v-model="rollingDays" class="bg-surface text-white px-2 py-1 rounded">
          <option v-for="d in [7, 14, 30, 90]" :value="d">{{ d }}</option>
        </select>
      </div>
      <VChart :option="rollingOption" style="height: 300px;" autoresize/>
    </div>

    <div v-if="hourProfileOption" class="card p-3 mb-4">
      <VChart :option="hourProfileOption" style="height: 300px;" autoresize/>
    </div>

    <div v-if="loading" class="p-2">{{ t('common.loading') }}</div>
    <div v-else-if="calls.length === 0" class="p-2 text-muted">{{ t('members.activity.empty', { year: selectedYear }) }}</div>
    <div v-else class="border border-rule rounded-lg overflow-hidden">
      <div class="grid grid-cols-3 gap-2 p-2 font-bold bg-surface">
        <div>{{ t('common.subject') }}</div>
        <div>{{ t('common.start') }}</div>
        <div>{{ t('common.end') }}</div>
      </div>
      <div v-for="call in calls" :key="call.call_id"
           class="grid grid-cols-3 gap-2 p-2 hover:bg-surface cursor-pointer border-t border-rule"
           @click="router.push({name: 'Call', params: {id: call.call_id}})">
        <div>{{ call.subjects }}</div>
        <div>{{ formatDateTime(call.start) }}</div>
        <div>{{ formatDateTime(call.end) }}</div>
      </div>
    </div>
  </div>
</template>
