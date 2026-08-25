<script setup lang="ts">
import {computed, onMounted, ref, watch} from "vue";
import VChart from "vue-echarts";
import {use} from "echarts/core";
import {CanvasRenderer} from "echarts/renderers";
import {LineChart, BarChart, PieChart, HeatmapChart} from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
  VisualMapComponent
} from "echarts/components";
import {
  getDailyCalls,
  getMemberDailyCalls,
  getCallGroups,
  getCallGroupsMonthly,
  getYearSummary,
  getMemberYearStats,
  getYearRange,
  getYearlySeries,
  getCallTimeProfile,
  getCallSubjects,
  getCallDurations,
  getAbortReasons,
  getQualificationCoverage,
  getTurnoutDistribution,
  getExerciseSummary,
  getExerciseSessions,
  getExerciseMemberStats,
  getYouthSummary,
  getYouthSessions,
  getCombinedMemberStats,
  getMembership,
  type DailyCallCount,
  type MemberDailyStats,
  type CallGroupCount,
  type CallGroupMonthCount,
  type YearSummary,
  type MemberYearStats,
  type YearlySeriesEntry,
  type CallTimeProfileEntry,
  type CallSubjectCount,
  type DurationBucket,
  type AbortReasonCount,
  type QualificationCoverage,
  type TurnoutBucket,
  type ExerciseSummary,
  type ExerciseSession,
  type ExerciseMemberStats,
  type YouthSummary,
  type YouthSession,
  type CombinedMemberStats,
  type MembershipEntry
} from "../api/statistics.ts";
import {listMembers} from "../api/members.ts";
import type {Member} from "../interfaces/Member.ts";
import {t} from "../i18n";
import router from "../router";
import {
  categoryAxis,
  chartBase,
  highlightYear,
  legend,
  screenTheme,
  title,
  tooltip,
  timeProfileGrid,
  valueAxis,
  zoom,
  SERIES_COLORS
} from "../scripts/charts.ts";

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  HeatmapChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
  VisualMapComponent
]);

const theme = screenTheme
const WEEKDAYS = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

const currentYear = new Date().getFullYear()
const selectedYear = ref(currentYear)
const yearsBack = ref(5)
const rollingDays = ref(30)
const selectedMember = ref<string>('')
const years = ref<number[]>([currentYear])

const members = ref<Member[]>([])
const dailyCalls = ref<DailyCallCount[]>([])
const memberDailyCalls = ref<MemberDailyStats[]>([])
const callGroups = ref<CallGroupCount[]>([])
const callGroupsMonthly = ref<CallGroupMonthCount[]>([])
const yearSummary = ref<YearSummary | null>(null)
const memberYearStats = ref<MemberYearStats[]>([])
const yearlySeries = ref<YearlySeriesEntry[]>([])
const timeProfile = ref<CallTimeProfileEntry[]>([])
const callSubjects = ref<CallSubjectCount[]>([])
const callDurations = ref<DurationBucket[]>([])
const abortReasons = ref<AbortReasonCount[]>([])
const coverage = ref<QualificationCoverage | null>(null)
const turnout = ref<TurnoutBucket[]>([])
const exerciseSummary = ref<ExerciseSummary | null>(null)
const exerciseSessions = ref<ExerciseSession[]>([])
const exerciseMembers = ref<ExerciseMemberStats[]>([])
const youthSummary = ref<YouthSummary | null>(null)
const youthSessions = ref<YouthSession[]>([])
const combined = ref<CombinedMemberStats[]>([])
const membership = ref<MembershipEntry[]>([])
const loading = ref(false)

const startDate = ref('')
const endDate = ref('')

async function loadYears() {
  const range = await getYearRange()
  const highest = Math.max(range.max_year, currentYear)
  years.value = Array.from({length: highest - range.min_year + 1}, (_, i) => highest - i)
  if (!years.value.includes(selectedYear.value)) selectedYear.value = highest
}

async function loadStats() {
  loading.value = true
  const year = selectedYear.value
  try {
    const [dc, cg, cgm, ys, mys, series, tp, subj, dur, abort, cov, to, es, esess, emem, yos, yosess, comb, mem] =
        await Promise.all([
          getDailyCalls(year, rollingDays.value),
          getCallGroups(year),
          getCallGroupsMonthly(year),
          getYearSummary(year),
          getMemberYearStats(year),
          getYearlySeries(year, yearsBack.value),
          getCallTimeProfile(year),
          getCallSubjects(year, 10),
          getCallDurations(year),
          getAbortReasons(year),
          getQualificationCoverage(year),
          getTurnoutDistribution(year),
          getExerciseSummary(year),
          getExerciseSessions(year),
          getExerciseMemberStats(year),
          getYouthSummary(year),
          getYouthSessions(year),
          getCombinedMemberStats(year),
          getMembership(year, yearsBack.value)
        ])
    dailyCalls.value = dc
    callGroups.value = cg
    callGroupsMonthly.value = cgm
    yearSummary.value = ys
    memberYearStats.value = mys
    yearlySeries.value = series
    timeProfile.value = tp
    callSubjects.value = subj
    callDurations.value = dur
    abortReasons.value = abort
    coverage.value = cov
    turnout.value = to
    exerciseSummary.value = es
    exerciseSessions.value = esess
    exerciseMembers.value = emem
    youthSummary.value = yos
    youthSessions.value = yosess
    combined.value = comb
    membership.value = mem
    await loadMemberStats()
  } finally {
    loading.value = false
  }
}

async function loadMemberStats() {
  memberDailyCalls.value = selectedMember.value
      ? await getMemberDailyCalls(selectedYear.value, rollingDays.value, selectedMember.value)
      : []
}

watch([selectedYear, yearsBack], () => loadStats())
watch(rollingDays, () => loadStats())
watch(selectedMember, () => loadMemberStats())

onMounted(async () => {
  members.value = await listMembers(false)
  await loadYears()
  await loadStats()
})

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

const seriesYears = computed(() => yearlySeries.value.map(e => e.year))
const previousYear = computed(() => yearlySeries.value.find(e => e.year === selectedYear.value - 1) ?? null)

/** Percentage change against the previous year, or null when there is nothing to compare to. */
function delta(current: number | undefined, previous: number | undefined): number | null {
  if (current === undefined || previous === undefined || !previous) return null
  return Math.round((current - previous) / previous * 100)
}

function deltaLabel(value: number | null): string {
  if (value === null) return ''
  return value > 0 ? `+${value} %` : `${value} %`
}

const summaryDeltas = computed(() => {
  const prev = previousYear.value
  return {
    calls: delta(yearSummary.value?.call_count, prev?.call_count),
    aborted: delta(yearSummary.value?.aborted, prev?.aborted),
    callHours: delta(yearSummary.value?.count_call_hours, prev?.call_hours),
    crewHours: delta(yearSummary.value?.count_crew_hours, prev?.crew_hours)
  }
})

const currentSeries = computed(() => yearlySeries.value.find(e => e.year === selectedYear.value) ?? null)

const dailyCallsChartOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.dailyCalls', {days: rollingDays.value}), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(filteredDailyCalls.value.map(d => d.day), theme),
  yAxis: [valueAxis(t('statistics.charts.count'), theme), valueAxis(t('statistics.charts.hours'), theme)],
  series: [
    {name: t('statistics.charts.calls'), type: 'line', data: filteredDailyCalls.value.map(d => d.call_count), smooth: true},
    {name: t('statistics.charts.hours'), type: 'line', yAxisIndex: 1, data: filteredDailyCalls.value.map(d => d.call_hours), smooth: true}
  ],
  legend: legend(theme, {top: 30}),
  grid: {left: '10%', right: '10%', top: 90},
  dataZoom: zoom(theme)
}))

const memberDailyChartOption = computed(() => {
  if (!filteredMemberDailyCalls.value.length) return null
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.memberDailyCalls', {member: selectedMember.value, days: rollingDays.value}), theme),
    tooltip: tooltip(theme),
    xAxis: categoryAxis(filteredMemberDailyCalls.value.map(d => d.day), theme),
    yAxis: [valueAxis(t('statistics.charts.count'), theme), valueAxis('%', theme, {max: 100})],
    series: [
      {name: t('statistics.charts.ownCalls'), type: 'line', data: filteredMemberDailyCalls.value.map(d => d.call_count), smooth: true},
      {name: t('statistics.charts.totalCalls'), type: 'line', data: filteredMemberDailyCalls.value.map(d => d.call_count_total), smooth: true},
      {name: t('statistics.charts.share'), type: 'line', yAxisIndex: 1, data: filteredMemberDailyCalls.value.map(d => d.call_count_percentage), smooth: true}
    ],
    legend: legend(theme, {top: 30}),
    grid: {left: '10%', right: '10%', top: 90},
    dataZoom: zoom(theme)
  }
})

const callGroupsPieOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.callGroups'), theme),
  tooltip: tooltip(theme, 'item'),
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: callGroups.value.map(g => ({name: g.group, value: g.call_count})),
    label: {color: theme.muted, fontSize: theme.fontSize}
  }],
  legend: legend(theme, {orient: 'vertical', right: 10, top: 'center'})
}))

const monthlyGroupsChartOption = computed(() => {
  const groups = [...new Set(callGroupsMonthly.value.map(d => d.group))]
  const months = [...new Set(callGroupsMonthly.value.map(d => d.month))].sort()
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.monthlyGroups'), theme),
    tooltip: tooltip(theme),
    xAxis: categoryAxis(months.map(m => m.substring(0, 7)), theme),
    yAxis: valueAxis(t('statistics.charts.count'), theme),
    series: groups.map(group => ({
      name: group,
      type: 'bar',
      stack: 'total',
      data: months.map(m => callGroupsMonthly.value.find(d => d.month === m && d.group === group)?.call_count ?? 0)
    })),
    legend: legend(theme, {top: 30}),
    grid: {left: '10%', right: '5%', top: 90},
    dataZoom: zoom(theme)
  }
})

const memberRankingChartOption = computed(() => {
  const sorted = [...memberYearStats.value].sort((a, b) => b.call_count - a.call_count)
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.memberRanking'), theme),
    tooltip: tooltip(theme),
    xAxis: categoryAxis(sorted.map(m => m.member_name), theme, 45),
    yAxis: [valueAxis(t('statistics.charts.calls'), theme), valueAxis(t('statistics.charts.hours'), theme)],
    series: [
      {name: t('statistics.charts.calls'), type: 'bar', data: sorted.map(m => m.call_count)},
      {name: t('statistics.charts.hours'), type: 'bar', yAxisIndex: 1, data: sorted.map(m => m.call_hours)}
    ],
    legend: legend(theme, {top: 30}),
    grid: {left: '10%', right: '10%', bottom: '20%', top: 90},
    dataZoom: zoom(theme)
  }
})

const yearComparisonOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.yearComparison'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(seriesYears.value, theme),
  yAxis: valueAxis(t('statistics.charts.calls'), theme),
  series: [{
    name: t('statistics.charts.calls'),
    type: 'bar',
    data: yearlySeries.value.map(e => ({
      value: e.call_count,
      itemStyle: {color: highlightYear([e.year], selectedYear.value)[0]}
    })),
    label: {show: true, position: 'top', color: theme.muted, fontSize: theme.fontSize}
  }],
  grid: {left: '10%', right: '5%', top: 70}
}))

const hoursComparisonOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.hoursComparison'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(seriesYears.value, theme),
  yAxis: valueAxis(t('statistics.charts.hours'), theme),
  series: [
    {name: t('statistics.charts.hours'), type: 'bar', data: yearlySeries.value.map(e => e.call_hours)},
    {name: t('statistics.charts.crewHours'), type: 'bar', data: yearlySeries.value.map(e => e.crew_hours)}
  ],
  legend: legend(theme, {top: 30}),
  grid: {left: '12%', right: '5%', top: 90}
}))

const crewComparisonOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.crewComparison'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(seriesYears.value, theme),
  yAxis: valueAxis(t('statistics.charts.crewSize'), theme),
  series: [{
    name: t('statistics.charts.crewSize'),
    type: 'line',
    data: yearlySeries.value.map(e => e.avg_crew),
    smooth: true,
    lineStyle: {width: theme.lineWidth},
    symbolSize: theme.symbolSize
  }],
  grid: {left: '10%', right: '5%', top: 70}
}))

const timeProfileOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.timeProfile'), theme),
  tooltip: tooltip(theme, 'item'),
  xAxis: {...categoryAxis(Array.from({length: 24}, (_, h) => `${h}`), theme), splitLine: {show: false}},
  yAxis: {...categoryAxis(WEEKDAYS, theme), splitLine: {show: false}},
  visualMap: {
    min: 0,
    max: Math.max(1, ...timeProfile.value.map(e => e.call_count)),
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: 0,
    textStyle: {color: theme.muted, fontSize: theme.fontSize},
    inRange: {color: ['#1e293b', '#f97316']}
  },
  series: [{
    type: 'heatmap',
    data: timeProfileGrid(timeProfile.value),
    label: {show: false}
  }],
  grid: {left: '8%', right: '5%', top: 70, bottom: 70}
}))

const topSubjectsOption = computed(() => {
  const sorted = [...callSubjects.value].reverse()
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.topSubjects'), theme),
    tooltip: tooltip(theme),
    xAxis: valueAxis(t('statistics.charts.count'), theme),
    yAxis: categoryAxis(sorted.map(s => s.name), theme),
    series: [{
      type: 'bar',
      data: sorted.map(s => s.call_count),
      label: {show: true, position: 'right', color: theme.muted, fontSize: theme.fontSize}
    }],
    grid: {left: '28%', right: '10%', top: 70}
  }
})

const durationsOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.durations'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(callDurations.value.map(d => d.bucket), theme),
  yAxis: valueAxis(t('statistics.charts.count'), theme),
  series: [{type: 'bar', data: callDurations.value.map(d => d.call_count)}],
  grid: {left: '10%', right: '5%', top: 70}
}))

const abortReasonsOption = computed(() => {
  if (!abortReasons.value.length) return null
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.abortReasons'), theme),
    tooltip: tooltip(theme, 'item'),
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: abortReasons.value.map(r => ({name: r.reason, value: r.call_count})),
      label: {color: theme.muted, fontSize: theme.fontSize}
    }],
    legend: legend(theme, {orient: 'vertical', right: 10, top: 'center'})
  }
})

const coverageOption = computed(() => {
  const c = coverage.value
  if (!c || !c.call_count) return null
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.qualificationCoverage'), theme),
    tooltip: tooltip(theme),
    xAxis: categoryAxis([t('statistics.charts.withLeader'), t('statistics.charts.withDriver'), t('statistics.charts.withBoth')], theme),
    yAxis: valueAxis('%', theme, {max: 100}),
    series: [{
      type: 'bar',
      data: [c.with_leader, c.with_driver, c.with_both].map(v => Math.round(v * 100 / c.call_count)),
      label: {show: true, position: 'top', formatter: '{c} %', color: theme.muted, fontSize: theme.fontSize}
    }],
    grid: {left: '10%', right: '5%', top: 70}
  }
})

const turnoutOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.turnout'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(turnout.value.map(b => b.bucket), theme),
  yAxis: valueAxis(t('statistics.charts.members'), theme),
  series: [{
    type: 'bar',
    data: turnout.value.map(b => b.member_count),
    label: {show: true, position: 'top', color: theme.muted, fontSize: theme.fontSize}
  }],
  grid: {left: '10%', right: '5%', top: 70}
}))

const exerciseAttendanceOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.exerciseAttendance'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(exerciseSessions.value.map(e => e.exercise_date), theme, 45),
  yAxis: valueAxis(t('statistics.charts.participants'), theme),
  series: [{type: 'bar', data: exerciseSessions.value.map(e => e.attendance)}],
  grid: {left: '10%', right: '5%', bottom: '22%', top: 70},
  dataZoom: zoom(theme)
}))

const exerciseRankingOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.exerciseRanking'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(exerciseMembers.value.map(m => m.member_name), theme, 45),
  yAxis: [valueAxis(t('statistics.charts.attendance'), theme), valueAxis('%', theme, {max: 100})],
  series: [
    {name: t('statistics.charts.attendance'), type: 'bar', data: exerciseMembers.value.map(m => m.attended)},
    {name: '%', type: 'line', yAxisIndex: 1, data: exerciseMembers.value.map(m => m.attended_perc)}
  ],
  legend: legend(theme, {top: 30}),
  grid: {left: '10%', right: '10%', bottom: '22%', top: 90},
  dataZoom: zoom(theme)
}))

const exerciseComparisonOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.exerciseComparison'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(seriesYears.value, theme),
  yAxis: [valueAxis(t('statistics.charts.exercises'), theme), valueAxis(t('statistics.charts.hours'), theme)],
  series: [
    {name: t('statistics.charts.exercises'), type: 'bar', data: yearlySeries.value.map(e => e.exercise_count)},
    {name: t('statistics.charts.hours'), type: 'line', yAxisIndex: 1, data: yearlySeries.value.map(e => e.exercise_hours)}
  ],
  legend: legend(theme, {top: 30}),
  grid: {left: '10%', right: '10%', top: 90}
}))

const youthSessionsOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.youthSessions'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(youthSessions.value.map(y => y.exercise_date), theme, 45),
  yAxis: valueAxis(t('statistics.charts.participants'), theme),
  series: [
    {name: t('statistics.charts.participants'), type: 'bar', data: youthSessions.value.map(y => y.participants)},
    {name: t('statistics.charts.instructors'), type: 'bar', data: youthSessions.value.map(y => y.instructors)}
  ],
  legend: legend(theme, {top: 30}),
  grid: {left: '10%', right: '5%', bottom: '22%', top: 90},
  dataZoom: zoom(theme)
}))

const youthComparisonOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.youthComparison'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(seriesYears.value, theme),
  yAxis: [valueAxis(t('statistics.charts.youth'), theme), valueAxis(t('statistics.charts.participants'), theme)],
  series: [
    {name: t('statistics.charts.youth'), type: 'bar', data: yearlySeries.value.map(e => e.youth_count)},
    {name: t('statistics.charts.participants'), type: 'line', yAxisIndex: 1, data: yearlySeries.value.map(e => e.youth_participants)}
  ],
  legend: legend(theme, {top: 30}),
  grid: {left: '10%', right: '10%', top: 90}
}))

const combinedOption = computed(() => {
  const top = combined.value.slice(0, 20)
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.combined'), theme),
    tooltip: tooltip(theme),
    xAxis: categoryAxis(top.map(m => m.member_name), theme, 45),
    yAxis: valueAxis(t('statistics.charts.hours'), theme),
    series: [
      {name: t('statistics.sections.calls'), type: 'bar', stack: 'total', data: top.map(m => m.call_hours)},
      {name: t('statistics.sections.exercises'), type: 'bar', stack: 'total', data: top.map(m => m.exercise_hours)},
      {name: t('statistics.sections.youth'), type: 'bar', stack: 'total', data: top.map(m => m.youth_hours)}
    ],
    legend: legend(theme, {top: 30}),
    grid: {left: '10%', right: '5%', bottom: '22%', top: 90},
    dataZoom: zoom(theme)
  }
})

const totalHoursComparisonOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.totalHoursComparison'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(seriesYears.value, theme),
  yAxis: valueAxis(t('statistics.charts.hours'), theme),
  series: [
    {name: t('statistics.sections.calls'), type: 'bar', stack: 'total', data: yearlySeries.value.map(e => e.call_hours)},
    {name: t('statistics.sections.exercises'), type: 'bar', stack: 'total', data: yearlySeries.value.map(e => e.exercise_hours)},
    {name: t('statistics.sections.youth'), type: 'bar', stack: 'total', data: yearlySeries.value.map(e => e.youth_hours)}
  ],
  legend: legend(theme, {top: 30}),
  grid: {left: '10%', right: '5%', top: 90}
}))

const membershipOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.membershipComparison'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(membership.value.map(m => m.year), theme),
  yAxis: valueAxis(t('statistics.charts.members'), theme),
  series: [
    {name: t('statistics.charts.roster'), type: 'bar', data: membership.value.map(m => m.roster_members), itemStyle: {color: SERIES_COLORS[7]}},
    {name: t('statistics.charts.participating'), type: 'bar', data: membership.value.map(m => m.participating_members)},
    {name: t('statistics.charts.retired'), type: 'line', data: membership.value.map(m => m.retired_in_year)}
  ],
  legend: legend(theme, {top: 30}),
  grid: {left: '10%', right: '5%', top: 90}
}))

function present() {
  router.push({name: 'Presentation', query: {year: selectedYear.value, years_back: yearsBack.value}})
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl">{{ t('statistics.title') }}</h1>
      <button @click="present" class="bg-orange-600 text-white px-4 py-2 rounded">{{ t('statistics.present') }}</button>
    </div>

    <div class="flex flex-wrap gap-4 items-end p-4 border border-gray-700 rounded-lg">
      <div>
        <label class="block text-sm text-gray-400">{{ t('common.year') }}</label>
        <select v-model="selectedYear" class="bg-gray-800 text-white px-3 py-2 rounded">
          <option v-for="y in years" :value="y">{{ y }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm text-gray-400">{{ t('statistics.yearsBack') }}</label>
        <select v-model="yearsBack" class="bg-gray-800 text-white px-3 py-2 rounded">
          <option v-for="n in [3, 5, 10]" :value="n">{{ n }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm text-gray-400">{{ t('statistics.rollingDays') }}</label>
        <select v-model="rollingDays" class="bg-gray-800 text-white px-3 py-2 rounded">
          <option v-for="d in [7, 14, 30, 60, 90, 180, 365]" :value="d">{{ d }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm text-gray-400">{{ t('common.from') }}</label>
        <input type="date" v-model="startDate" class="bg-gray-800 text-white px-3 py-2 rounded"/>
      </div>
      <div>
        <label class="block text-sm text-gray-400">{{ t('common.to') }}</label>
        <input type="date" v-model="endDate" class="bg-gray-800 text-white px-3 py-2 rounded"/>
      </div>
      <div>
        <label class="block text-sm text-gray-400">{{ t('statistics.member') }}</label>
        <select v-model="selectedMember" class="bg-gray-800 text-white px-3 py-2 rounded">
          <option value="">{{ t('common.all') }}</option>
          <option v-for="m in members" :value="m.name">{{ m.name }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="text-center p-8">{{ t('common.loading') }}</div>

    <template v-else>
      <h2 class="text-xl text-gray-300">{{ t('statistics.sections.calls') }}</h2>

      <div v-if="yearSummary" class="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-orange-400">{{ yearSummary.call_count }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.summary.calls') }}</div>
          <div class="text-xs text-gray-500">{{ deltaLabel(summaryDeltas.calls) }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-red-400">{{ yearSummary.aborted }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.summary.aborted') }}</div>
          <div class="text-xs text-gray-500">{{ deltaLabel(summaryDeltas.aborted) }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-green-400">{{ yearSummary.count_call_hours }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.summary.callHours') }}</div>
          <div class="text-xs text-gray-500">{{ deltaLabel(summaryDeltas.callHours) }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-blue-400">{{ yearSummary.count_crew_hours }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.summary.crewHours') }}</div>
          <div class="text-xs text-gray-500">{{ deltaLabel(summaryDeltas.crewHours) }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-cyan-400">{{ currentSeries?.avg_crew ?? '-' }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.callExtras.avgCrew') }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-purple-400">{{ yearSummary.half_hours_members ?? '-' }}%</div>
          <div class="text-sm text-gray-400">{{ t('statistics.summary.halfShare') }}</div>
        </div>
      </div>

      <div class="bg-gray-900 rounded-lg p-4">
        <VChart :option="yearComparisonOption" style="height: 320px;" autoresize/>
      </div>

      <div class="bg-gray-900 rounded-lg p-4">
        <VChart :option="dailyCallsChartOption" style="height: 350px;" autoresize/>
      </div>

      <div v-if="memberDailyChartOption" class="bg-gray-900 rounded-lg p-4">
        <VChart :option="memberDailyChartOption" style="height: 350px;" autoresize/>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="callGroupsPieOption" style="height: 350px;" autoresize/>
        </div>
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="monthlyGroupsChartOption" style="height: 350px;" autoresize/>
        </div>
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="topSubjectsOption" style="height: 380px;" autoresize/>
        </div>
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="timeProfileOption" style="height: 380px;" autoresize/>
        </div>
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="durationsOption" style="height: 320px;" autoresize/>
        </div>
        <div v-if="coverageOption" class="bg-gray-900 rounded-lg p-4">
          <VChart :option="coverageOption" style="height: 320px;" autoresize/>
        </div>
        <div v-if="abortReasonsOption" class="bg-gray-900 rounded-lg p-4">
          <VChart :option="abortReasonsOption" style="height: 320px;" autoresize/>
        </div>
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="crewComparisonOption" style="height: 320px;" autoresize/>
        </div>
      </div>

      <div class="bg-gray-900 rounded-lg p-4">
        <VChart :option="hoursComparisonOption" style="height: 320px;" autoresize/>
      </div>

      <div class="bg-gray-900 rounded-lg p-4">
        <VChart :option="memberRankingChartOption" style="height: 400px;" autoresize/>
      </div>

      <h2 class="text-xl text-gray-300">{{ t('statistics.sections.exercises') }}</h2>

      <div v-if="exerciseSummary" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-orange-400">{{ exerciseSummary.exercise_count }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.exerciseSummary.count') }}</div>
          <div class="text-xs text-gray-500">{{ deltaLabel(delta(currentSeries?.exercise_count, previousYear?.exercise_count)) }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-green-400">{{ exerciseSummary.exercise_hours }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.exerciseSummary.hours') }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-blue-400">{{ exerciseSummary.avg_attendance }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.exerciseSummary.avgAttendance') }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-purple-400">{{ exerciseSummary.crew_hours }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.exerciseSummary.crewHours') }}</div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="exerciseAttendanceOption" style="height: 350px;" autoresize/>
        </div>
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="exerciseComparisonOption" style="height: 350px;" autoresize/>
        </div>
      </div>

      <div class="bg-gray-900 rounded-lg p-4">
        <VChart :option="exerciseRankingOption" style="height: 400px;" autoresize/>
      </div>

      <h2 class="text-xl text-gray-300">{{ t('statistics.sections.youth') }}</h2>

      <div v-if="youthSummary" class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-orange-400">{{ youthSummary.session_count }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.youthSummary.count') }}</div>
          <div class="text-xs text-gray-500">{{ deltaLabel(delta(currentSeries?.youth_count, previousYear?.youth_count)) }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-green-400">{{ youthSummary.session_hours }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.youthSummary.hours') }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-blue-400">{{ youthSummary.avg_participants }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.youthSummary.avgParticipants') }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-cyan-400">{{ youthSummary.instructor_count }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.youthSummary.instructors') }}</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-3xl font-bold text-purple-400">{{ youthSummary.instructor_hours }}</div>
          <div class="text-sm text-gray-400">{{ t('statistics.youthSummary.instructorHours') }}</div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="youthSessionsOption" style="height: 350px;" autoresize/>
        </div>
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="youthComparisonOption" style="height: 350px;" autoresize/>
        </div>
      </div>

      <h2 class="text-xl text-gray-300">{{ t('statistics.sections.overall') }}</h2>

      <div class="bg-gray-900 rounded-lg p-4">
        <VChart :option="combinedOption" style="height: 420px;" autoresize/>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="turnoutOption" style="height: 320px;" autoresize/>
        </div>
        <div class="bg-gray-900 rounded-lg p-4">
          <VChart :option="totalHoursComparisonOption" style="height: 320px;" autoresize/>
        </div>
      </div>

      <div class="bg-gray-900 rounded-lg p-4">
        <VChart :option="membershipOption" style="height: 320px;" autoresize/>
      </div>
      <p class="text-xs text-gray-500">{{ t('statistics.rosterCaveat') }}</p>
    </template>
  </div>
</template>
