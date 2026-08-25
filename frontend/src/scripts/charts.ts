import {t} from '../i18n'

export const SERIES_COLORS = ['#f97316', '#22c55e', '#38bdf8', '#a78bfa', '#facc15', '#f43f5e', '#2dd4bf', '#94a3b8']

export const HIGHLIGHT_COLOR = '#f97316'
export const MUTED_COLOR = '#475569'

export interface ChartTheme {
    text: string
    muted: string
    fontSize: number
    titleSize: number
    lineWidth: number
    symbolSize: number
    interactive: boolean
}

export const screenTheme: ChartTheme = {
    text: '#fff',
    muted: '#ccc',
    fontSize: 12,
    titleSize: 18,
    lineWidth: 2,
    symbolSize: 4,
    interactive: true
}

export const presentationTheme: ChartTheme = {
    text: '#fff',
    muted: '#cbd5e1',
    fontSize: 20,
    titleSize: 34,
    lineWidth: 5,
    symbolSize: 10,
    interactive: false
}

export function title(text: string, theme: ChartTheme) {
    return {text, left: 'center', textStyle: {color: theme.text, fontSize: theme.titleSize}}
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
        splitLine: {lineStyle: {color: 'rgba(148, 163, 184, 0.2)'}},
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
            saveAsImage: {title: t('statistics.toolbox.save'), backgroundColor: '#111827'},
            dataView: {title: t('statistics.toolbox.data'), readOnly: true, lang: [t('statistics.toolbox.data'), t('common.close'), '']},
            restore: {title: t('statistics.toolbox.restore')}
        }
    }
}

export function zoom(theme: ChartTheme) {
    if (!theme.interactive) return undefined
    return [{type: 'inside'}, {type: 'slider', textStyle: {color: theme.muted}}]
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
