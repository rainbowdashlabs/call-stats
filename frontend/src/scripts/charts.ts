import {reactive} from 'vue'
import {t} from '../i18n'

/**
 * Categorical series colours, mid-lightness so they hold up on both the paper and the steel
 * ground. Signal red is deliberately absent: red in this interface means something went wrong.
 */
export const SERIES_COLORS = ['#1f6f8b', '#c2703d', '#4e7a3f', '#7b5ea7', '#b03a5b', '#2e8c8c', '#8a6e2f', '#5c6775']

function token(name: string, fallback: string): string {
    if (typeof document === 'undefined') return fallback
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback
}

/**
 * Fixed colours for the call groups, so a group reads the same in every chart that splits by
 * group. Anything not listed falls back to the palette, picked deterministically from the name.
 */
const GROUP_COLORS: Record<string, string> = {
    BRAND: '#dc2626',
    TH: '#3b82f6',
    RD: '#22c55e',
    FR: '#86efac',
    MISC: '#facc15'
}

export function groupColor(group: string): string {
    const fixed = GROUP_COLORS[group.toUpperCase()]
    if (fixed) return fixed
    const hash = [...group].reduce((sum, char) => sum + char.charCodeAt(0), 0)
    return SERIES_COLORS[hash % SERIES_COLORS.length]!
}

const GROUP_LABEL_KEYS: Record<string, string> = {
    MISC: 'statistics.groups.misc'
}

/** The name a call group carries in the UI, which is not always what the database calls it. */
export function groupLabel(group: string): string {
    const key = GROUP_LABEL_KEYS[group.toUpperCase()]
    return key ? t(key) : group
}

/** Abort reasons are stored as full sentences ("Kein Fahrzeug"); the charts only need the noun. */
export function abortReasonLabel(reason: string): string {
    return reason.replace(/^Kein(e|er)? /, '')
}

/** Whether an abort reason says that people or equipment were missing. */
export function isShortageReason(reason: string): boolean {
    return /^Kein(e|er)? /.test(reason)
}

/** The selected year in a comparison chart. Ink, not red — red is reserved for what went wrong. */
export let HIGHLIGHT_COLOR = '#10141a'
export let MUTED_COLOR = '#c3cad3'

export interface ChartTheme {
    text: string
    muted: string
    fontSize: number
    titleSize: number
    lineWidth: number
    symbolSize: number
    interactive: boolean
}

export const screenTheme: ChartTheme = reactive({
    text: '#10141a',
    muted: '#5c6775',
    fontSize: 12,
    titleSize: 18,
    lineWidth: 2,
    symbolSize: 4,
    interactive: true
})

/** The deck always runs on the dark ground, whatever the app is set to. */
export const presentationTheme: ChartTheme = {
    text: '#edf0f3',
    muted: '#cbd5e1',
    fontSize: 20,
    titleSize: 34,
    lineWidth: 5,
    symbolSize: 10,
    interactive: false
}

/**
 * ECharts wants literal colours, so the token values are read out of the document and pushed
 * into the reactive screen theme whenever the app switches between light and dark.
 */
export function refreshChartTheme() {
    screenTheme.text = token('--c-ink', '#10141a')
    screenTheme.muted = token('--c-muted', '#5c6775')
    HIGHLIGHT_COLOR = token('--c-ink', '#10141a')
    MUTED_COLOR = token('--c-rule', '#dce1e7')
}

if (typeof document !== 'undefined') {
    refreshChartTheme()
    new MutationObserver(refreshChartTheme).observe(document.documentElement, {attributeFilter: ['data-theme']})
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', refreshChartTheme)
}

export function title(text: string, theme: ChartTheme) {
    return {text, left: 'center', top: 0, textStyle: {color: theme.text, fontSize: theme.titleSize}}
}

export function categoryAxis(data: (string | number)[], theme: ChartTheme, rotate = 0) {
    return {
        type: 'category',
        data,
        axisLabel: {color: theme.muted, fontSize: theme.fontSize, rotate},
        axisLine: {lineStyle: {color: theme.muted}}
    }
}

export function valueAxis(name: string, theme: ChartTheme, extra: object = {}) {
    return {
        type: 'value',
        name,
        nameGap: theme.fontSize * 1.8,
        axisLabel: {color: theme.muted, fontSize: theme.fontSize},
        nameTextStyle: {color: theme.muted, fontSize: theme.fontSize},
        splitLine: {lineStyle: {color: 'color-mix(in srgb, currentColor 0%, rgb(148 163 184 / 0.25))'}},
        ...extra
    }
}

export function legend(theme: ChartTheme, extra: object = {}) {
    return {textStyle: {color: theme.muted, fontSize: theme.fontSize}, ...extra}
}

export function tooltip(theme: ChartTheme, trigger: 'axis' | 'item' = 'axis') {
    return {trigger, textStyle: {fontSize: theme.fontSize}}
}

/** Save-as-image, a data table and a zoom reset — only worth showing off a projector. */
export function toolbox(theme: ChartTheme) {
    if (!theme.interactive) return undefined
    return {
        right: 10,
        iconStyle: {borderColor: theme.muted},
        feature: {
            saveAsImage: {title: t('statistics.toolbox.save'), backgroundColor: token('--c-surface', '#ffffff')},
            dataView: {title: t('statistics.toolbox.data'), readOnly: true, lang: [t('statistics.toolbox.data'), t('common.close'), '']},
            restore: {title: t('statistics.toolbox.restore')}
        }
    }
}

export function zoom(theme: ChartTheme) {
    if (!theme.interactive) return undefined
    return [{type: 'inside'}, {type: 'slider', height: 16, bottom: 8, textStyle: {color: theme.muted}}]
}

/** Paints the selected year in the accent colour and every other year muted. */
export function highlightYear(years: number[], selected: number) {
    return years.map(year => year === selected ? HIGHLIGHT_COLOR : MUTED_COLOR)
}

export function chartBase(theme: ChartTheme) {
    const base = {
        color: SERIES_COLORS,
        backgroundColor: 'transparent',
        textStyle: {fontSize: theme.fontSize},
        animationDuration: theme.interactive ? 300 : 900
    }
    const feature = toolbox(theme)
    return feature ? {...base, toolbox: feature} : base
}

/**
 * Fills a complete 7 × 24 grid so every weekday and hour is painted from the colour scale.
 * Without it, hours that never saw a call fall back to the axis background and read as
 * lighter than the hours that did.
 */
export function timeProfileGrid(entries: { weekday: number, hour: number, call_count: number }[]): number[][] {
    const counts = new Map(entries.map(e => [`${e.weekday}:${e.hour}`, e.call_count]))
    const grid: number[][] = []
    for (let weekday = 1; weekday <= 7; weekday++) {
        for (let hour = 0; hour < 24; hour++) {
            grid.push([hour, weekday - 1, counts.get(`${weekday}:${hour}`) ?? 0])
        }
    }
    return grid
}
