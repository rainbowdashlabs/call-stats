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
  getCallStrengths,
  getStrengthByHour,
  getCallGroupsYearly,
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
  type MembershipEntry,
  type CallStrength,
  type StrengthByHour,
  type CallGroupYearCount
} from "../api/statistics.ts";
import {listMembers} from "../api/members.ts";
import type {Member} from "../interfaces/Member.ts";
import {t} from "../i18n";
import router from "../router";
import StandardButton from "../components/base/buttons/StandardButton.vue";
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
  SERIES_COLORS,
  groupColor,
  groupLabel,
  abortReasonLabel,
  isShortageReason
} from "../scripts/charts.ts";
import {formatDayTime} from "../scripts/datetime.ts";

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
const callStrengths = ref<CallStrength[]>([])
const strengthByHour = ref<StrengthByHour[]>([])
const groupsYearly = ref<CallGroupYearCount[]>([])
const rollingMetric = ref<'count' | 'hours' | 'percent'>('count')
const seriesVisible = ref(true)
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
    const [dc, cg, cgm, ys, mys, series, tp, subj, dur, abort, cov, to, es, esess, emem, yos, yosess, comb, mem,
           mdc, strengths, byHour, groupYears] =
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
          getMembership(year, yearsBack.value),
          getMemberDailyCalls(year, rollingDays.value),
          getCallStrengths(year),
          getStrengthByHour(year),
          getCallGroupsYearly(year, yearsBack.value)
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
    memberDailyCalls.value = mdc
    callStrengths.value = strengths
    strengthByHour.value = byHour
    groupsYearly.value = groupYears
  } finally {
    loading.value = false
  }
}

watch([selectedYear, yearsBack], () => loadStats())
watch(rollingDays, () => loadStats())

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
  legend: legend(theme, {top: 40}),
  grid: {left: '10%', right: '10%', top: 90, bottom: 66},
  dataZoom: zoom(theme)
}))

function rollingValue(row: MemberDailyStats): number {
  if (rollingMetric.value === 'hours') return row.call_hours
  if (rollingMetric.value === 'percent') return row.call_count_percentage
  return row.call_count
}

const rollingSeries = computed(() => {
  const rows = filteredMemberDailyCalls.value
      .filter(d => !selectedMember.value || d.name === selectedMember.value)
  const days = [...new Set(rows.map(d => d.day))].sort()
  const names = [...new Set(rows.map(d => d.name))].sort()
  const values = new Map<string, Map<string, number>>()
  for (const row of rows) {
    if (!values.has(row.name)) values.set(row.name, new Map())
    values.get(row.name)!.set(row.day, rollingValue(row))
  }
  return {days, names, values}
})

/** Drives the button that switches every member line off and on again at once. */
const legendSelection = computed(() =>
    Object.fromEntries(rollingSeries.value.names.map(name => [name, seriesVisible.value])))

const memberRollingOption = computed(() => {
  const {days, names, values} = rollingSeries.value
  if (!days.length) return null
  const percent = rollingMetric.value === 'percent'
  const series: object[] = names.map(name => ({
    name,
    type: 'line',
    smooth: true,
    showSymbol: false,
    emphasis: {focus: 'series'},
    lineStyle: {width: 1.5, opacity: 0.75},
    data: days.map(day => values.get(name)?.get(day) ?? 0)
  }))
  if (!percent) {
    const totals = new Map(filteredDailyCalls.value.map(d =>
        [d.day, (rollingMetric.value === 'hours' ? d.call_hours : d.call_count) ?? 0]))
    series.push({
      name: t('statistics.charts.total'),
      type: 'line',
      smooth: true,
      showSymbol: false,
      z: 5,
      lineStyle: {type: 'dashed', width: theme.lineWidth + 1},
      itemStyle: {color: '#f87171'},
      data: days.map(day => totals.get(day) ?? 0)
    })
  }
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.memberRolling', {days: rollingDays.value}), theme),
    tooltip: {...tooltip(theme), order: 'valueDesc'},
    xAxis: categoryAxis(days, theme),
    yAxis: valueAxis(percent ? '%' : t(`statistics.charts.${rollingMetric.value === 'hours' ? 'hours' : 'count'}`),
        theme, percent ? {max: 100} : {}),
    series,
    legend: legend(theme, {top: 30, type: 'scroll', selected: legendSelection.value}),
    grid: {left: '10%', right: '5%', top: 110, bottom: 60},
    dataZoom: zoom(theme)
  }
})

/** Stärke je Einsatz, eingefärbt danach, ob Führung und Maschinist dabei waren (Grafana 22). */
const callStrengthsOption = computed(() => {
  const rows = callStrengths.value
  if (!rows.length) return null
  const barColor = (row: CallStrength) => row.leader > 0 && row.driver > 0 ? '#22c55e'
      : row.leader > 0 || row.driver > 0 ? '#f59e0b' : '#ef4444'
  const mark = (value: number) => value > 0 ? '✔' : '—'
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.callStrengths'), theme),
    tooltip: {
      ...tooltip(theme, 'item'),
      formatter: (params: {dataIndex: number, name: string}) => {
        const row = rows[params.dataIndex]!
        return `${params.name}<br/>${t('statistics.charts.strength')}: ${row.strength}`
            + `<br/>${t('statistics.charts.leader')}: ${mark(row.leader)}`
            + `<br/>${t('statistics.charts.driver')}: ${mark(row.driver)}`
      }
    },
    xAxis: categoryAxis(rows.map(r => formatDayTime(r.start)), theme, 45),
    yAxis: valueAxis(t('statistics.charts.strength'), theme),
    series: [{
      name: t('statistics.charts.strength'),
      type: 'bar',
      data: rows.map(r => ({value: r.strength, itemStyle: {color: barColor(r)}}))
    }],
    grid: {left: '10%', right: '5%', top: 70, bottom: 132},
    dataZoom: zoom(theme)
  }
})

/** Wie stark die Wehr zu welcher Tageszeit ausrückt (Grafana 45). */
const strengthByHourOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.strengthByHour'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(strengthByHour.value.map(h => `${String(h.hour).padStart(2, '0')}:00`), theme),
  yAxis: valueAxis(t('statistics.charts.strength'), theme, {min: 0}),
  series: [
    {name: t('statistics.charts.avgStrength'), type: 'line', smooth: true, data: strengthByHour.value.map(h => h.avg_strength)},
    {name: t('statistics.charts.medianStrength'), type: 'line', smooth: true, data: strengthByHour.value.map(h => h.median_strength)},
    {name: t('statistics.charts.p10Strength'), type: 'line', smooth: true, data: strengthByHour.value.map(h => h.p10_strength)}
  ],
  legend: legend(theme, {top: 40}),
  grid: {left: '10%', right: '5%', top: 90, bottom: 66}
}))

/** Abbrüche, bei denen Personal oder Gerät gefehlt hat (Grafana 23). */
const shortageOption = computed(() => {
  const shortages = abortReasons.value.filter(r => isShortageReason(r.reason))
  if (!shortages.length) return null
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.shortage'), theme),
    tooltip: tooltip(theme, 'item'),
    series: [{
      type: 'pie',
      radius: ['38%', '66%'],
      center: ['34%', '54%'],
      data: shortages.map(r => ({name: abortReasonLabel(r.reason), value: r.call_count})),
      label: {color: theme.muted, fontSize: theme.fontSize}
    }],
    legend: legend(theme, {orient: 'vertical', right: 10, top: 'center'})
  }
})

/** Stichwortgruppen über mehrere Jahre (Grafana 47). */
const groupsYearlyOption = computed(() => {
  const years = [...new Set(groupsYearly.value.map(e => e.year))].sort()
  const groups = [...new Set(groupsYearly.value.map(e => e.group))].sort()
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.groupsYearly'), theme),
    tooltip: tooltip(theme),
    xAxis: categoryAxis(years, theme),
    yAxis: valueAxis(t('statistics.charts.count'), theme),
    series: groups.map(group => ({
      name: groupLabel(group),
      type: 'line',
      smooth: true,
      itemStyle: {color: groupColor(group)},
      data: years.map(year => groupsYearly.value.find(e => e.year === year && e.group === group)?.call_count ?? 0)
    })),
    legend: legend(theme, {top: 40}),
    grid: {left: '10%', right: '5%', top: 90, bottom: 66}
  }
})

const callGroupsPieOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.callGroups'), theme),
  tooltip: tooltip(theme, 'item'),
  series: [{
    type: 'pie',
    radius: ['38%', '66%'],
      center: ['34%', '54%'],
    data: callGroups.value.map(g => ({
      name: groupLabel(g.group),
      value: g.call_count,
      itemStyle: {color: groupColor(g.group)}
    })),
    label: {color: theme.muted, fontSize: theme.fontSize}
  }],
  legend: legend(theme, {orient: 'vertical', right: 10, top: 'center'})
}))

const callGroupsBarOption = computed(() => {
  const sorted = [...callGroups.value].sort((a, b) => b.call_count - a.call_count)
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.callGroups'), theme),
    tooltip: tooltip(theme),
    xAxis: categoryAxis(sorted.map(g => groupLabel(g.group)), theme),
    yAxis: valueAxis(t('statistics.charts.count'), theme),
    series: [{
      type: 'bar',
      data: sorted.map(g => ({value: g.call_count, itemStyle: {color: groupColor(g.group)}})),
      label: {show: true, position: 'top', color: theme.muted, fontSize: theme.fontSize}
    }],
    grid: {left: '10%', right: '5%', top: 70, bottom: 66}
  }
})

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
      name: groupLabel(group),
      type: 'bar',
      stack: 'total',
      itemStyle: {color: groupColor(group)},
      data: months.map(m => callGroupsMonthly.value.find(d => d.month === m && d.group === group)?.call_count ?? 0)
    })),
    legend: legend(theme, {top: 40}),
    grid: {left: '10%', right: '5%', top: 90, bottom: 66},
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
    yAxis: [
      valueAxis(t('statistics.charts.calls'), theme),
      valueAxis(t('statistics.charts.hours'), theme),
      valueAxis('%', theme, {max: 100, position: 'right', offset: 55, splitLine: {show: false}})
    ],
    series: [
      {name: t('statistics.charts.calls'), type: 'bar', data: sorted.map(m => m.call_count)},
      {name: t('statistics.charts.hours'), type: 'bar', yAxisIndex: 1, data: sorted.map(m => m.call_hours)},
      {name: t('statistics.charts.percentCalls'), type: 'line', yAxisIndex: 2, symbolSize: theme.symbolSize,
        data: sorted.map(m => m.call_count_perc)},
      {name: t('statistics.charts.percentHours'), type: 'line', yAxisIndex: 2, symbolSize: theme.symbolSize,
        data: sorted.map(m => m.call_hours_perc)}
    ],
    legend: legend(theme, {top: 40}),
    grid: {left: '10%', right: '14%', bottom: 132, top: 90},
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
  grid: {left: '10%', right: '5%', top: 70, bottom: 66}
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
  legend: legend(theme, {top: 40}),
  grid: {left: '12%', right: '5%', top: 90, bottom: 66}
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
  grid: {left: '10%', right: '5%', top: 70, bottom: 66}
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
    bottom: 4,
    textStyle: {color: theme.muted, fontSize: theme.fontSize},
    inRange: {color: ['#1e293b', '#f97316']}
  },
  series: [{
    type: 'heatmap',
    data: timeProfileGrid(timeProfile.value),
    label: {show: false}
  }],
  grid: {left: '8%', right: '5%', top: 70, bottom: 96}
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
    grid: {left: '28%', right: '10%', top: 70, bottom: 66}
  }
})

const durationsOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.durations'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(callDurations.value.map(d => d.bucket), theme),
  yAxis: valueAxis(t('statistics.charts.count'), theme),
  series: [{type: 'bar', data: callDurations.value.map(d => d.call_count)}],
  grid: {left: '10%', right: '5%', top: 70, bottom: 66}
}))

const abortReasonsOption = computed(() => {
  if (!abortReasons.value.length) return null
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.abortReasons'), theme),
    tooltip: tooltip(theme, 'item'),
    series: [{
      type: 'pie',
      radius: ['38%', '66%'],
      center: ['34%', '54%'],
      data: abortReasons.value.map(r => ({name: abortReasonLabel(r.reason), value: r.call_count})),
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
    grid: {left: '10%', right: '5%', top: 70, bottom: 66}
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
  grid: {left: '10%', right: '5%', top: 70, bottom: 66}
}))

const exerciseAttendanceOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.exerciseAttendance'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(exerciseSessions.value.map(e => e.exercise_date), theme, 45),
  yAxis: valueAxis(t('statistics.charts.participants'), theme),
  series: [{type: 'bar', data: exerciseSessions.value.map(e => e.attendance)}],
  grid: {left: '10%', right: '5%', bottom: 132, top: 70},
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
  legend: legend(theme, {top: 40}),
  grid: {left: '10%', right: '10%', bottom: 132, top: 90},
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
  legend: legend(theme, {top: 40}),
  grid: {left: '10%', right: '10%', top: 90, bottom: 66}
}))

const youthSessionsOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.youthSessions'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(youthSessions.value.map(y => y.exercise_date), theme, 45),
  yAxis: [
    valueAxis(t('statistics.charts.participants'), theme),
    valueAxis(t('statistics.charts.ratio'), theme, {position: 'right', splitLine: {show: false}})
  ],
  series: [
    {name: t('statistics.charts.participants'), type: 'bar', data: youthSessions.value.map(y => y.participants)},
    {name: t('statistics.charts.instructors'), type: 'bar', data: youthSessions.value.map(y => y.instructors)},
    {
      name: t('statistics.charts.ratio'), type: 'line', yAxisIndex: 1, symbolSize: theme.symbolSize,
      data: youthSessions.value.map(y => y.instructors ? Math.round(y.participants / y.instructors * 10) / 10 : 0)
    }
  ],
  legend: legend(theme, {top: 40}),
  grid: {left: '10%', right: '5%', bottom: 132, top: 90},
  dataZoom: zoom(theme)
}))

const youthComparisonOption = computed(() => ({
  ...chartBase(theme),
  title: title(t('statistics.charts.youthComparison'), theme),
  tooltip: tooltip(theme),
  xAxis: categoryAxis(seriesYears.value, theme),
  yAxis: [
    valueAxis(t('statistics.charts.youth'), theme),
    valueAxis(t('statistics.charts.participants'), theme),
    valueAxis(t('statistics.charts.ratio'), theme, {position: 'right', offset: 55, splitLine: {show: false}})
  ],
  series: [
    {name: t('statistics.charts.youth'), type: 'bar', data: yearlySeries.value.map(e => e.youth_count)},
    {name: t('statistics.charts.participants'), type: 'line', yAxisIndex: 1, data: yearlySeries.value.map(e => e.youth_participants)},
    {
      name: t('statistics.charts.ratio'), type: 'line', yAxisIndex: 2, symbolSize: theme.symbolSize,
      data: yearlySeries.value.map(e => e.youth_instructors
          ? Math.round(e.youth_participants / e.youth_instructors * 10) / 10 : 0)
    }
  ],
  legend: legend(theme, {top: 40}),
  grid: {left: '10%', right: '10%', top: 90, bottom: 66}
}))

const youthRankingOption = computed(() => {
  const instructors = combined.value.filter(m => m.youth_count > 0)
      .sort((a, b) => b.youth_count - a.youth_count)
  if (!instructors.length) return null
  return {
    ...chartBase(theme),
    title: title(t('statistics.charts.youthRanking'), theme),
    tooltip: tooltip(theme),
    xAxis: categoryAxis(instructors.map(m => m.member_name), theme, 45),
    yAxis: [valueAxis(t('statistics.charts.youth'), theme), valueAxis(t('statistics.charts.hours'), theme)],
    series: [
      {name: t('statistics.charts.youth'), type: 'bar', data: instructors.map(m => m.youth_count),
        itemStyle: {color: '#fb923c'}},
      {name: t('statistics.charts.hours'), type: 'bar', yAxisIndex: 1, data: instructors.map(m => m.youth_hours)}
    ],
    legend: legend(theme, {top: 40}),
    grid: {left: '10%', right: '10%', bottom: 132, top: 90},
    dataZoom: zoom(theme)
  }
})

type HoursColumn = 'member_name' | 'call_hours' | 'exercise_hours' | 'youth_hours' | 'total_hours'

const hoursSort = ref<HoursColumn>('total_hours')

const hoursRows = computed(() => [...combined.value].sort((a, b) => hoursSort.value === 'member_name'
    ? a.member_name.localeCompare(b.member_name)
    : (b[hoursSort.value] as number) - (a[hoursSort.value] as number)))

const hoursTotals = computed(() => hoursRows.value.reduce((sum, row) => ({
  call_hours: sum.call_hours + row.call_hours,
  exercise_hours: sum.exercise_hours + row.exercise_hours,
  youth_hours: sum.youth_hours + row.youth_hours,
  total_hours: sum.total_hours + row.total_hours
}), {call_hours: 0, exercise_hours: 0, youth_hours: 0, total_hours: 0}))

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
    legend: legend(theme, {top: 40}),
    grid: {left: '10%', right: '5%', bottom: 132, top: 90},
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
  legend: legend(theme, {top: 40}),
  grid: {left: '10%', right: '5%', top: 90, bottom: 66}
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
    {name: t('statistics.charts.joined'), type: 'line', data: membership.value.map(m => m.joined_in_year)},
    {name: t('statistics.charts.retired'), type: 'line', data: membership.value.map(m => m.retired_in_year)}
  ],
  legend: legend(theme, {top: 40}),
  grid: {left: '10%', right: '5%', top: 90, bottom: 66}
}))

function present() {
  router.push({name: 'Presentation', query: {year: selectedYear.value, years_back: yearsBack.value}})
}
</script>

<template>
  <div class="flex flex-col gap-8 pb-10">
    <div class="flex items-end justify-between gap-6">
      <div>
        <div class="eyebrow">{{ t('statistics.eyebrow') }}</div>
        <h1 class="headline text-4xl mt-1">{{ t('statistics.title') }}</h1>
      </div>
      <StandardButton @click="present">
        <font-awesome-icon icon="fa-solid fa-display"/>
        {{ t('statistics.present') }}
      </StandardButton>
    </div>

    <div class="card flex flex-wrap gap-5 items-end p-5">
      <div>
        <label class="label block mb-1.5">{{ t('common.year') }}</label>
        <select v-model="selectedYear" class="field mt-2" style="width: auto">
          <option v-for="y in years" :value="y">{{ y }}</option>
        </select>
      </div>
      <div>
        <label class="label block mb-1.5">{{ t('statistics.yearsBack') }}</label>
        <select v-model="yearsBack" class="field mt-2" style="width: auto">
          <option v-for="n in [3, 5, 10]" :value="n">{{ n }}</option>
        </select>
      </div>
      <div>
        <label class="label block mb-1.5">{{ t('statistics.rollingDays') }}</label>
        <select v-model="rollingDays" class="field mt-2" style="width: auto">
          <option v-for="d in [7, 14, 30, 60, 90, 180, 365]" :value="d">{{ d }}</option>
        </select>
      </div>
      <div>
        <label class="label block mb-1.5">{{ t('common.from') }}</label>
        <input type="date" v-model="startDate" class="field mt-2" style="width: auto"/>
      </div>
      <div>
        <label class="label block mb-1.5">{{ t('common.to') }}</label>
        <input type="date" v-model="endDate" class="field mt-2" style="width: auto"/>
      </div>
      <div>
        <label class="label block mb-1.5">{{ t('statistics.rollingMetric.label') }}</label>
        <select v-model="rollingMetric" class="field mt-2" style="width: auto">
          <option value="count">{{ t('statistics.rollingMetric.count') }}</option>
          <option value="hours">{{ t('statistics.rollingMetric.hours') }}</option>
          <option value="percent">{{ t('statistics.rollingMetric.percent') }}</option>
        </select>
      </div>
      <div>
        <label class="label block mb-1.5">{{ t('statistics.member') }}</label>
        <select v-model="selectedMember" class="field mt-2" style="width: auto">
          <option value="">{{ t('common.all') }}</option>
          <option v-for="m in members" :value="m.name">{{ m.name }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="p-12 text-center text-muted">{{ t('common.loading') }}</div>

    <template v-else>
      <h2 class="headline text-2xl mt-4 pt-4 border-t border-rule">{{ t('statistics.sections.calls') }}</h2>

      <div v-if="yearSummary" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ yearSummary.call_count }}</div>
          <div class="label mt-1">{{ t('statistics.summary.calls') }}</div>
          <div class="tabular text-xs text-muted mt-1">{{ deltaLabel(summaryDeltas.calls) }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular" style="color: var(--c-signal-ink)">{{ yearSummary.aborted }}</div>
          <div class="label mt-1">{{ t('statistics.summary.aborted') }}</div>
          <div class="tabular text-xs text-muted mt-1">{{ deltaLabel(summaryDeltas.aborted) }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ yearSummary.count_call_hours }}</div>
          <div class="label mt-1">{{ t('statistics.summary.callHours') }}</div>
          <div class="tabular text-xs text-muted mt-1">{{ deltaLabel(summaryDeltas.callHours) }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ yearSummary.count_crew_hours }}</div>
          <div class="label mt-1">{{ t('statistics.summary.crewHours') }}</div>
          <div class="tabular text-xs text-muted mt-1">{{ deltaLabel(summaryDeltas.crewHours) }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ currentSeries?.avg_crew ?? '-' }}</div>
          <div class="label mt-1">{{ t('statistics.callExtras.avgCrew') }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ yearSummary.half_hours_members ?? '-' }}%</div>
          <div class="label mt-1">{{ t('statistics.summary.halfShare') }}</div>
        </div>
      </div>

      <div class="card p-5 md:p-6">
        <VChart :option="yearComparisonOption" style="height: 320px;" autoresize/>
      </div>

      <div class="card p-5 md:p-6">
        <VChart :option="dailyCallsChartOption" style="height: 350px;" autoresize/>
      </div>

      <div v-if="memberRollingOption" class="card p-5 md:p-6">
        <div class="flex justify-end">
          <button @click="seriesVisible = !seriesVisible"
                  class="text-sm text-muted hover:text-ink border border-rule rounded px-2 py-1">
            {{ t('statistics.toggleSeries') }}
          </button>
        </div>
        <VChart :option="memberRollingOption" style="height: 420px;" autoresize/>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="card p-5 md:p-6">
          <VChart :option="callGroupsPieOption" style="height: 350px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="callGroupsBarOption" style="height: 350px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="monthlyGroupsChartOption" style="height: 350px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="topSubjectsOption" style="height: 380px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="timeProfileOption" style="height: 380px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="durationsOption" style="height: 320px;" autoresize/>
        </div>
        <div v-if="coverageOption" class="card p-5 md:p-6">
          <VChart :option="coverageOption" style="height: 320px;" autoresize/>
        </div>
        <div v-if="abortReasonsOption" class="card p-5 md:p-6">
          <VChart :option="abortReasonsOption" style="height: 320px;" autoresize/>
        </div>
        <div v-if="shortageOption" class="card p-5 md:p-6">
          <VChart :option="shortageOption" style="height: 320px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="strengthByHourOption" style="height: 320px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="groupsYearlyOption" style="height: 320px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="crewComparisonOption" style="height: 320px;" autoresize/>
        </div>
      </div>

      <div class="card p-5 md:p-6">
        <VChart :option="hoursComparisonOption" style="height: 320px;" autoresize/>
      </div>

      <div v-if="callStrengthsOption" class="card p-5 md:p-6">
        <VChart :option="callStrengthsOption" style="height: 380px;" autoresize/>
      </div>

      <div class="card p-5 md:p-6">
        <VChart :option="memberRankingChartOption" style="height: 400px;" autoresize/>
      </div>

      <h2 class="headline text-2xl mt-4 pt-4 border-t border-rule">{{ t('statistics.sections.exercises') }}</h2>

      <div v-if="exerciseSummary" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ exerciseSummary.exercise_count }}</div>
          <div class="label mt-1">{{ t('statistics.exerciseSummary.count') }}</div>
          <div class="tabular text-xs text-muted mt-1">{{ deltaLabel(delta(currentSeries?.exercise_count, previousYear?.exercise_count)) }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ exerciseSummary.exercise_hours }}</div>
          <div class="label mt-1">{{ t('statistics.exerciseSummary.hours') }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ exerciseSummary.avg_attendance }}</div>
          <div class="label mt-1">{{ t('statistics.exerciseSummary.avgAttendance') }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ exerciseSummary.crew_hours }}</div>
          <div class="label mt-1">{{ t('statistics.exerciseSummary.crewHours') }}</div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="card p-5 md:p-6">
          <VChart :option="exerciseAttendanceOption" style="height: 350px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="exerciseComparisonOption" style="height: 350px;" autoresize/>
        </div>
      </div>

      <div class="card p-5 md:p-6">
        <VChart :option="exerciseRankingOption" style="height: 400px;" autoresize/>
      </div>

      <h2 class="headline text-2xl mt-4 pt-4 border-t border-rule">{{ t('statistics.sections.youth') }}</h2>

      <div v-if="youthSummary" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ youthSummary.session_count }}</div>
          <div class="label mt-1">{{ t('statistics.youthSummary.count') }}</div>
          <div class="tabular text-xs text-muted mt-1">{{ deltaLabel(delta(currentSeries?.youth_count, previousYear?.youth_count)) }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ youthSummary.session_hours }}</div>
          <div class="label mt-1">{{ t('statistics.youthSummary.hours') }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ youthSummary.avg_participants }}</div>
          <div class="label mt-1">{{ t('statistics.youthSummary.avgParticipants') }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ youthSummary.instructor_count }}</div>
          <div class="label mt-1">{{ t('statistics.youthSummary.instructors') }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ youthSummary.instructor_hours }}</div>
          <div class="label mt-1">{{ t('statistics.youthSummary.instructorHours') }}</div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="card p-5 md:p-6">
          <VChart :option="youthSessionsOption" style="height: 350px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="youthComparisonOption" style="height: 350px;" autoresize/>
        </div>
        <div v-if="youthRankingOption" class="card p-5 md:p-6 md:col-span-2">
          <VChart :option="youthRankingOption" style="height: 350px;" autoresize/>
        </div>
      </div>

      <h2 class="headline text-2xl mt-4 pt-4 border-t border-rule">{{ t('statistics.sections.overall') }}</h2>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ hoursTotals.call_hours }}</div>
          <div class="label mt-1">{{ t('statistics.table.calls') }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ hoursTotals.exercise_hours }}</div>
          <div class="label mt-1">{{ t('statistics.table.exercises') }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="text-3xl font-bold text-amber-400">{{ hoursTotals.youth_hours }}</div>
          <div class="label mt-1">{{ t('statistics.table.youth') }}</div>
        </div>
        <div class="card p-4 text-center">
          <div class="headline text-4xl tabular">{{ hoursTotals.total_hours }}</div>
          <div class="label mt-1">{{ t('statistics.table.total') }}</div>
        </div>
      </div>

      <div class="card p-5 md:p-6">
        <VChart :option="combinedOption" style="height: 420px;" autoresize/>
      </div>

      <div class="card p-5 md:p-6 overflow-x-auto">
        <div class="text-lg mb-3">{{ t('statistics.table.title') }}</div>
        <table class="w-full text-sm">
          <thead class="text-muted">
          <tr>
            <th class="text-left py-1 cursor-pointer" @click="hoursSort = 'member_name'">{{ t('statistics.table.name') }}</th>
            <th class="text-right py-1 cursor-pointer" @click="hoursSort = 'call_hours'">{{ t('statistics.table.calls') }}</th>
            <th class="text-right py-1 cursor-pointer" @click="hoursSort = 'exercise_hours'">{{ t('statistics.table.exercises') }}</th>
            <th class="text-right py-1 cursor-pointer" @click="hoursSort = 'youth_hours'">{{ t('statistics.table.youth') }}</th>
            <th class="text-right py-1 cursor-pointer" @click="hoursSort = 'total_hours'">{{ t('statistics.table.total') }}</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="row in hoursRows" :key="row.member_id" class="border-t border-rule">
            <td class="py-1">{{ row.member_name }}</td>
            <td class="text-right">{{ row.call_hours }}</td>
            <td class="text-right">{{ row.exercise_hours }}</td>
            <td class="text-right">{{ row.youth_hours }}</td>
            <td class="text-right font-bold">{{ row.total_hours }}</td>
          </tr>
          </tbody>
          <tfoot class="border-t-2 border-rule font-bold">
          <tr>
            <td class="py-1">{{ t('statistics.table.sum') }}</td>
            <td class="text-right">{{ hoursTotals.call_hours }}</td>
            <td class="text-right">{{ hoursTotals.exercise_hours }}</td>
            <td class="text-right">{{ hoursTotals.youth_hours }}</td>
            <td class="text-right">{{ hoursTotals.total_hours }}</td>
          </tr>
          </tfoot>
        </table>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="card p-5 md:p-6">
          <VChart :option="turnoutOption" style="height: 320px;" autoresize/>
        </div>
        <div class="card p-5 md:p-6">
          <VChart :option="totalHoursComparisonOption" style="height: 320px;" autoresize/>
        </div>
      </div>

      <div class="card p-5 md:p-6">
        <VChart :option="membershipOption" style="height: 320px;" autoresize/>
      </div>
      <p class="tabular text-xs text-muted mt-1">{{ t('statistics.rosterCaveat') }}</p>
    </template>
  </div>
</template>
