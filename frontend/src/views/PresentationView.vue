<script setup lang="ts">
import {computed, onMounted, onUnmounted, ref} from "vue";
import VChart from "vue-echarts";
import {use} from "echarts/core";
import {CanvasRenderer} from "echarts/renderers";
import {LineChart, BarChart, PieChart, HeatmapChart} from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent
} from "echarts/components";
import {getPresentation, type PresentationData} from "../api/statistics.ts";
import {t} from "../i18n";
import router from "../router";
import {useRoute} from "vue-router";
import {
  categoryAxis,
  chartBase,
  highlightYear,
  legend,
  presentationTheme,
  timeProfileGrid,
  title,
  tooltip,
  valueAxis,
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
  VisualMapComponent
]);

const theme = presentationTheme
const WEEKDAYS = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
const AUTO_ADVANCE_MS = 12000

const route = useRoute()
const year = Number(route.query.year) || new Date().getFullYear()
const yearsBack = Number(route.query.years_back) || 5

const data = ref<PresentationData | null>(null)
const loading = ref(true)
const index = ref(0)
const showOverview = ref(false)
const auto = ref(false)
let autoTimer: number | undefined

interface Tile {
  value: string | number
  label: string
}

interface Slide {
  section: string
  heading: string
  tiles?: Tile[]
  option?: any
  closing?: string
}

const series = computed(() => data.value?.yearly_series ?? [])
const seriesYears = computed(() => series.value.map(e => e.year))
const currentSeries = computed(() => series.value.find(e => e.year === year) ?? null)

function comparisonBars(name: string, values: number[]) {
  return {
    name,
    type: 'bar',
    data: values.map((value, i) => ({
      value,
      itemStyle: {color: highlightYear([seriesYears.value[i]!], year)[0]}
    })),
    label: {show: true, position: 'top', color: theme.muted, fontSize: theme.fontSize}
  }
}

function base(heading: string) {
  return {
    ...chartBase(theme),
    title: title(heading, theme),
    tooltip: tooltip(theme),
    legend: legend(theme, {top: 60}),
    grid: {left: '10%', right: '6%', top: 150, bottom: 80}
  }
}

const slides = computed<Slide[]>(() => {
  const d = data.value
  if (!d) return []
  const calls = t('statistics.sections.calls')
  const exercises = t('statistics.sections.exercises')
  const youth = t('statistics.sections.youth')
  const overall = t('statistics.sections.overall')
  const result: Slide[] = []

  result.push({
    section: t('presentation.slides.titleSlide'),
    heading: t('presentation.title', {year}),
    tiles: [
      {value: d.call_summary?.call_count ?? 0, label: t('statistics.summary.calls')},
      {value: d.exercise_summary.exercise_count, label: t('statistics.exerciseSummary.count')},
      {value: d.youth_summary.session_count, label: t('statistics.youthSummary.count')}
    ]
  })

  if (d.call_summary && d.call_summary.call_count > 0) {
    result.push({
      section: calls,
      heading: t('presentation.slides.callsNumbers', {year}),
      tiles: [
        {value: d.call_summary.call_count, label: t('statistics.summary.calls')},
        {value: d.call_summary.count_call_hours, label: t('statistics.summary.callHours')},
        {value: d.call_summary.count_crew_hours, label: t('statistics.summary.crewHours')},
        {value: d.call_summary.aborted, label: t('statistics.summary.aborted')},
        {value: currentSeries.value?.avg_crew ?? 0, label: t('statistics.callExtras.avgCrew')}
      ]
    })

    const months = [...new Set(d.call_groups_monthly.map(e => e.month))].sort()
    const groups = [...new Set(d.call_groups_monthly.map(e => e.group))]
    result.push({
      section: calls,
      heading: t('presentation.slides.callsMonthly'),
      option: {
        ...base(t('presentation.slides.callsMonthly')),
        xAxis: categoryAxis(months.map(m => m.substring(0, 7)), theme),
        yAxis: valueAxis(t('statistics.charts.count'), theme),
        series: groups.map(group => ({
          name: group,
          type: 'bar',
          stack: 'total',
          data: months.map(m => d.call_groups_monthly.find(e => e.month === m && e.group === group)?.call_count ?? 0)
        }))
      }
    })

    result.push({
      section: calls,
      heading: t('presentation.slides.callsGroups'),
      option: {
        ...chartBase(theme),
        title: title(t('presentation.slides.callsGroups'), theme),
        tooltip: tooltip(theme, 'item'),
        legend: legend(theme, {orient: 'vertical', right: 40, top: 'center'}),
        series: [{
          type: 'pie',
          radius: ['35%', '65%'],
          data: d.call_groups.map(g => ({name: g.group, value: g.call_count})),
          label: {color: theme.muted, fontSize: theme.fontSize, formatter: '{b}: {c}'}
        }]
      }
    })

    if (d.call_subjects.length) {
      const sorted = [...d.call_subjects].reverse()
      result.push({
        section: calls,
        heading: t('presentation.slides.callsSubjects'),
        option: {
          ...base(t('presentation.slides.callsSubjects')),
          xAxis: valueAxis(t('statistics.charts.count'), theme),
          yAxis: categoryAxis(sorted.map(s => s.name), theme),
          series: [{
            type: 'bar',
            data: sorted.map(s => s.call_count),
            label: {show: true, position: 'right', color: theme.muted, fontSize: theme.fontSize}
          }],
          grid: {left: '32%', right: '10%', top: 150, bottom: 80}
        }
      })
    }

    result.push({
      section: calls,
      heading: t('presentation.slides.callsTime'),
      option: {
        ...chartBase(theme),
        title: title(t('presentation.slides.callsTime'), theme),
        tooltip: tooltip(theme, 'item'),
        xAxis: {...categoryAxis(Array.from({length: 24}, (_, h) => `${h}`), theme), splitLine: {show: false}},
        yAxis: {...categoryAxis(WEEKDAYS, theme), splitLine: {show: false}},
        visualMap: {
          min: 0,
          max: Math.max(1, ...d.call_time_profile.map(e => e.call_count)),
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: 10,
          textStyle: {color: theme.muted, fontSize: theme.fontSize},
          inRange: {color: ['#1e293b', '#f97316']}
        },
        series: [{type: 'heatmap', data: timeProfileGrid(d.call_time_profile)}],
        grid: {left: '8%', right: '6%', top: 150, bottom: 130}
      }
    })

    const coverage = d.qualification_coverage
    if (coverage.call_count > 0) {
      result.push({
        section: calls,
        heading: t('presentation.slides.callsCoverage'),
        option: {
          ...base(t('presentation.slides.callsCoverage')),
          xAxis: categoryAxis([t('statistics.charts.withLeader'), t('statistics.charts.withDriver'), t('statistics.charts.withBoth')], theme),
          yAxis: valueAxis('%', theme, {max: 100}),
          series: [{
            type: 'bar',
            data: [coverage.with_leader, coverage.with_driver, coverage.with_both]
                .map(v => Math.round(v * 100 / coverage.call_count)),
            label: {show: true, position: 'top', formatter: '{c} %', color: theme.muted, fontSize: theme.fontSize}
          }]
        }
      })
    }

    result.push({
      section: `${calls} — ${t('statistics.sections.comparison')}`,
      heading: t('presentation.slides.callsYears'),
      option: {
        ...base(t('presentation.slides.callsYears')),
        xAxis: categoryAxis(seriesYears.value, theme),
        yAxis: valueAxis(t('statistics.charts.calls'), theme),
        series: [comparisonBars(t('statistics.charts.calls'), series.value.map(e => e.call_count))],
        legend: undefined
      }
    })

    result.push({
      section: `${calls} — ${t('statistics.sections.comparison')}`,
      heading: t('presentation.slides.callsHoursYears'),
      option: {
        ...base(t('presentation.slides.callsHoursYears')),
        xAxis: categoryAxis(seriesYears.value, theme),
        yAxis: valueAxis(t('statistics.charts.hours'), theme),
        series: [
          {name: t('statistics.summary.callHours'), type: 'bar', data: series.value.map(e => e.call_hours)},
          {name: t('statistics.summary.crewHours'), type: 'bar', data: series.value.map(e => e.crew_hours)}
        ]
      }
    })

    result.push({
      section: `${calls} — ${t('statistics.sections.comparison')}`,
      heading: t('presentation.slides.callsCrewYears'),
      option: {
        ...base(t('presentation.slides.callsCrewYears')),
        xAxis: categoryAxis(seriesYears.value, theme),
        yAxis: valueAxis(t('statistics.charts.crewSize'), theme),
        series: [comparisonBars(t('statistics.charts.crewSize'), series.value.map(e => e.avg_crew))],
        legend: undefined
      }
    })
  }

  if (d.exercise_summary.exercise_count > 0) {
    result.push({
      section: exercises,
      heading: t('presentation.slides.exercisesNumbers', {year}),
      tiles: [
        {value: d.exercise_summary.exercise_count, label: t('statistics.exerciseSummary.count')},
        {value: d.exercise_summary.exercise_hours, label: t('statistics.exerciseSummary.hours')},
        {value: d.exercise_summary.avg_attendance, label: t('statistics.exerciseSummary.avgAttendance')},
        {value: d.exercise_summary.crew_hours, label: t('statistics.exerciseSummary.crewHours')}
      ]
    })

    result.push({
      section: exercises,
      heading: t('presentation.slides.exercisesAttendance'),
      option: {
        ...base(t('presentation.slides.exercisesAttendance')),
        xAxis: categoryAxis(d.exercise_sessions.map(e => e.exercise_date), theme, 45),
        yAxis: valueAxis(t('statistics.charts.participants'), theme),
        series: [{type: 'bar', data: d.exercise_sessions.map(e => e.attendance)}],
        legend: undefined,
        grid: {left: '10%', right: '6%', top: 150, bottom: 160}
      }
    })

    const ranked = d.exercise_member_stats.filter(m => m.attended > 0)
    result.push({
      section: exercises,
      heading: t('presentation.slides.exercisesRanking'),
      option: {
        ...base(t('presentation.slides.exercisesRanking')),
        xAxis: categoryAxis(ranked.map(m => m.member_name), theme, 45),
        yAxis: valueAxis(t('statistics.charts.attendance'), theme),
        series: [{
          type: 'bar',
          data: ranked.map(m => m.attended),
          label: {show: true, position: 'top', color: theme.muted, fontSize: theme.fontSize}
        }],
        legend: undefined,
        grid: {left: '10%', right: '6%', top: 150, bottom: 200}
      }
    })

    result.push({
      section: `${exercises} — ${t('statistics.sections.comparison')}`,
      heading: t('presentation.slides.exercisesYears'),
      option: {
        ...base(t('presentation.slides.exercisesYears')),
        xAxis: categoryAxis(seriesYears.value, theme),
        yAxis: valueAxis(t('statistics.charts.exercises'), theme),
        series: [comparisonBars(t('statistics.charts.exercises'), series.value.map(e => e.exercise_count))],
        legend: undefined
      }
    })

    result.push({
      section: `${exercises} — ${t('statistics.sections.comparison')}`,
      heading: t('presentation.slides.exercisesAttendanceYears'),
      option: {
        ...base(t('presentation.slides.exercisesAttendanceYears')),
        xAxis: categoryAxis(seriesYears.value, theme),
        yAxis: valueAxis(t('statistics.charts.participants'), theme),
        series: [
          {
            name: t('statistics.exerciseSummary.avgAttendance'),
            type: 'bar',
            data: series.value.map(e => e.exercise_count ? Math.round(e.exercise_attendance / e.exercise_count) : 0)
          },
          {name: t('statistics.charts.participating'), type: 'line', data: series.value.map(e => e.participating_members)}
        ]
      }
    })
  }

  if (d.youth_summary.session_count > 0) {
    result.push({
      section: youth,
      heading: t('presentation.slides.youthNumbers', {year}),
      tiles: [
        {value: d.youth_summary.session_count, label: t('statistics.youthSummary.count')},
        {value: d.youth_summary.session_hours, label: t('statistics.youthSummary.hours')},
        {value: d.youth_summary.avg_participants, label: t('statistics.youthSummary.avgParticipants')},
        {value: d.youth_summary.instructor_count, label: t('statistics.youthSummary.instructors')},
        {value: d.youth_summary.instructor_hours, label: t('statistics.youthSummary.instructorHours')}
      ]
    })

    result.push({
      section: youth,
      heading: t('presentation.slides.youthSessions'),
      option: {
        ...base(t('presentation.slides.youthSessions')),
        xAxis: categoryAxis(d.youth_sessions.map(y => y.exercise_date), theme, 45),
        yAxis: valueAxis(t('statistics.charts.participants'), theme),
        series: [
          {name: t('statistics.charts.participants'), type: 'bar', data: d.youth_sessions.map(y => y.participants)},
          {name: t('statistics.charts.instructors'), type: 'bar', data: d.youth_sessions.map(y => y.instructors)}
        ],
        grid: {left: '10%', right: '6%', top: 150, bottom: 160}
      }
    })

    result.push({
      section: `${youth} — ${t('statistics.sections.comparison')}`,
      heading: t('presentation.slides.youthYears'),
      option: {
        ...base(t('presentation.slides.youthYears')),
        xAxis: categoryAxis(seriesYears.value, theme),
        yAxis: [valueAxis(t('statistics.charts.youth'), theme), valueAxis(t('statistics.charts.participants'), theme)],
        series: [
          {name: t('statistics.charts.youth'), type: 'bar', data: series.value.map(e => e.youth_count)},
          {name: t('statistics.charts.participants'), type: 'line', yAxisIndex: 1, data: series.value.map(e => e.youth_participants)}
        ]
      }
    })

    result.push({
      section: `${youth} — ${t('statistics.sections.comparison')}`,
      heading: t('presentation.slides.youthInstructorYears'),
      option: {
        ...base(t('presentation.slides.youthInstructorYears')),
        xAxis: categoryAxis(seriesYears.value, theme),
        yAxis: valueAxis(t('statistics.charts.hours'), theme),
        series: [comparisonBars(t('statistics.charts.hours'), series.value.map(e => e.youth_hours))],
        legend: undefined
      }
    })
  }

  const top = d.combined_member_stats.slice(0, 20)
  if (top.length) {
    result.push({
      section: overall,
      heading: t('presentation.slides.overallCombined'),
      option: {
        ...base(t('presentation.slides.overallCombined')),
        xAxis: categoryAxis(top.map(m => m.member_name), theme, 45),
        yAxis: valueAxis(t('statistics.charts.hours'), theme),
        series: [
          {name: calls, type: 'bar', stack: 'total', data: top.map(m => m.call_hours)},
          {name: exercises, type: 'bar', stack: 'total', data: top.map(m => m.exercise_hours)},
          {name: youth, type: 'bar', stack: 'total', data: top.map(m => m.youth_hours)}
        ],
        grid: {left: '10%', right: '6%', top: 150, bottom: 200}
      }
    })
  }

  result.push({
    section: overall,
    heading: t('presentation.slides.overallTurnout'),
    option: {
      ...base(t('presentation.slides.overallTurnout')),
      xAxis: categoryAxis(d.turnout_distribution.map(b => b.bucket), theme),
      yAxis: valueAxis(t('statistics.charts.members'), theme),
      series: [{
        type: 'bar',
        data: d.turnout_distribution.map(b => b.member_count),
        label: {show: true, position: 'top', color: theme.muted, fontSize: theme.fontSize}
      }],
      legend: undefined
    }
  })

  const thisYearMembership = d.membership.find(m => m.year === year)
  if (thisYearMembership) {
    result.push({
      section: overall,
      heading: t('presentation.slides.overallMembership', {year}),
      tiles: [
        {value: thisYearMembership.roster_members, label: t('statistics.charts.roster')},
        {value: thisYearMembership.participating_members, label: t('statistics.charts.participating')},
        {value: thisYearMembership.joined_in_year, label: t('statistics.charts.joined')},
        {value: thisYearMembership.retired_in_year, label: t('statistics.charts.retired')}
      ]
    })
  }

  result.push({
    section: `${overall} — ${t('statistics.sections.comparison')}`,
    heading: t('presentation.slides.overallHoursYears'),
    option: {
      ...base(t('presentation.slides.overallHoursYears')),
      xAxis: categoryAxis(seriesYears.value, theme),
      yAxis: valueAxis(t('statistics.charts.hours'), theme),
      series: [
        {name: calls, type: 'bar', stack: 'total', data: series.value.map(e => e.call_hours)},
        {name: exercises, type: 'bar', stack: 'total', data: series.value.map(e => e.exercise_hours)},
        {name: youth, type: 'bar', stack: 'total', data: series.value.map(e => e.youth_hours)}
      ]
    }
  })

  result.push({
    section: `${overall} — ${t('statistics.sections.comparison')}`,
    heading: t('presentation.slides.overallMembershipYears'),
    option: {
      ...base(t('presentation.slides.overallMembershipYears')),
      xAxis: categoryAxis(d.membership.map(m => m.year), theme),
      yAxis: valueAxis(t('statistics.charts.members'), theme),
      series: [
        {name: t('statistics.charts.roster'), type: 'bar', data: d.membership.map(m => m.roster_members), itemStyle: {color: SERIES_COLORS[7]}},
        {name: t('statistics.charts.participating'), type: 'bar', data: d.membership.map(m => m.participating_members)},
        {name: t('statistics.charts.joined'), type: 'line', data: d.membership.map(m => m.joined_in_year)}
      ]
    }
  })

  const totalHours = (currentSeries.value?.call_hours ?? 0)
      + (currentSeries.value?.exercise_hours ?? 0)
      + (currentSeries.value?.youth_hours ?? 0)
  result.push({
    section: overall,
    heading: t('presentation.slides.closing', {year}),
    closing: t('presentation.closing', {
      calls: d.call_summary?.call_count ?? 0,
      exercises: d.exercise_summary.exercise_count,
      youth: d.youth_summary.session_count,
      hours: totalHours
    })
  })

  return result
})

const slide = computed(() => slides.value[index.value] ?? null)

function go(delta: number) {
  const count = slides.value.length
  if (!count) return
  index.value = Math.min(count - 1, Math.max(0, index.value + delta))
}

function jump(target: number) {
  index.value = target
  showOverview.value = false
}

async function toggleFullscreen() {
  if (document.fullscreenElement) {
    await document.exitFullscreen()
  } else {
    await document.documentElement.requestFullscreen().catch(() => undefined)
  }
}

function toggleAuto() {
  auto.value = !auto.value
  window.clearInterval(autoTimer)
  if (auto.value) {
    autoTimer = window.setInterval(() => {
      if (index.value >= slides.value.length - 1) {
        toggleAuto()
      } else {
        go(1)
      }
    }, AUTO_ADVANCE_MS)
  }
}

async function leave() {
  if (document.fullscreenElement) await document.exitFullscreen().catch(() => undefined)
  await router.push({name: 'Statistics'})
}

function onKey(e: KeyboardEvent) {
  const key = e.key
  if (key === 'ArrowRight' || key === ' ' || key === 'PageDown') {
    e.preventDefault()
    go(1)
  } else if (key === 'ArrowLeft' || key === 'PageUp') {
    e.preventDefault()
    go(-1)
  } else if (key === 'Home') {
    index.value = 0
  } else if (key === 'End') {
    index.value = slides.value.length - 1
  } else if (key === 'Escape') {
    if (showOverview.value) showOverview.value = false
    else void leave()
  } else if (key.toLowerCase() === 'o') {
    showOverview.value = !showOverview.value
  } else if (key.toLowerCase() === 'f') {
    void toggleFullscreen()
  } else if (key.toLowerCase() === 'p') {
    toggleAuto()
  }
}

onMounted(async () => {
  window.addEventListener('keydown', onKey)
  try {
    data.value = await getPresentation(year, yearsBack)
  } finally {
    loading.value = false
  }
  await document.documentElement.requestFullscreen().catch(() => undefined)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  window.clearInterval(autoTimer)
})
</script>

<template>
  <div class="fixed inset-0 flex flex-col z-50" style="background: #0b0f14; color: #edf0f3">
    <div v-if="loading" class="flex-1 flex items-center justify-center text-3xl">{{ t('common.loading') }}</div>

    <template v-else-if="slide">
      <div class="flex items-center justify-between px-8 pt-6 text-lg" style="color: #8892a0">
        <span>{{ slide.section }}</span>
        <div class="flex items-center gap-4">
          <span v-if="auto">{{ t('presentation.autoOn') }}</span>
          <span>{{ index + 1 }} / {{ slides.length }}</span>
          <button @click="leave" class="deck-button">{{ t('presentation.exit') }}</button>
        </div>
      </div>

      <div class="flex-1 flex flex-col items-center justify-center px-10 min-h-0">
        <template v-if="slide.tiles">
          <h1 class="headline text-6xl mb-14 text-center">{{ slide.heading }}</h1>
          <div class="flex flex-wrap justify-center gap-10">
            <div v-for="tile in slide.tiles" :key="tile.label"
                 class="deck-tile">
              <div class="headline text-7xl tabular">{{ tile.value }}</div>
              <div class="text-2xl mt-4" style="color: #8892a0">{{ tile.label }}</div>
            </div>
          </div>
        </template>

        <template v-else-if="slide.closing">
          <h1 class="headline text-6xl mb-14 text-center">{{ slide.heading }}</h1>
          <p class="text-4xl text-center max-w-5xl leading-relaxed" style="color: #cbd5e1">{{ slide.closing }}</p>
        </template>

        <VChart v-else-if="slide.option" :key="index" :option="slide.option" class="w-full h-full" autoresize/>
      </div>

      <div class="px-8 pb-5">
        <div class="h-1 rounded" style="background: #212932">
          <div class="h-1 bg-signal rounded transition-all"
               :style="{width: `${(index + 1) / slides.length * 100}%`}"/>
        </div>
        <div class="text-center text-sm mt-3" style="color: #5c6775">{{ t('presentation.hint') }}</div>
      </div>

      <div v-if="showOverview" class="absolute inset-0 bg-[#0b0f14]/95 overflow-y-auto p-10">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button v-for="(s, i) in slides" :key="i" @click="jump(i)"
                  class="deck-card"
                  :class="i === index ? 'deck-card-current' : ''">
            <div class="text-xs" style="color: #8892a0">{{ i + 1 }} · {{ s.section }}</div>
            <div class="text-lg mt-1">{{ s.heading }}</div>
          </button>
        </div>
      </div>
    </template>

    <div v-else class="flex-1 flex items-center justify-center text-3xl" style="color: #8892a0">
      {{ t('statistics.noData', {year}) }}
    </div>
  </div>
</template>

<style scoped>
.deck-button {
  padding: 5px 13px;
  border: 1px solid #2a333e;
  border-radius: 3px;
  background: #1a2027;
  color: #edf0f3;
  font-size: 14px;
  cursor: pointer;
}

.deck-button:hover {
  background: #212932;
}

.deck-tile {
  min-width: 14rem;
  padding: 40px 48px;
  text-align: center;
  background: #151b22;
  border: 1px solid #212932;
  border-radius: 6px;
}

.deck-card {
  text-align: left;
  padding: 16px;
  background: #151b22;
  border: 1px solid #212932;
  border-radius: 6px;
  cursor: pointer;
  color: #edf0f3;
}

.deck-card:hover {
  background: #1a2027;
}

.deck-card-current {
  border-color: #e0331f;
}
</style>
