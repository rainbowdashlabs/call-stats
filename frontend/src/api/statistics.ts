import {getHttpClient} from "./http.ts";
import {emitError} from "../events/bus.ts";

const http = getHttpClient()

export interface DailyCallCount {
    day: string
    call_count: number
    call_hours: number | null
}

export interface MemberDailyStats {
    day: string
    id: number
    name: string
    call_count: number
    call_count_total: number
    call_count_percentage: number
    call_hours: number
    call_hours_total: number
    call_hours_percentage: number
}

export interface CallGroupCount {
    group: string
    call_count: number
}

export interface CallGroupMonthCount {
    month: string
    group: string
    call_count: number
}

export interface YearSummary {
    call_count: number
    aborted: number
    count_call_hours: number
    count_crew_hours: number
    half_hours_members: number | null
}

export interface MemberYearStats {
    member_name: string
    call_count: number
    call_hours: number
    call_count_perc: number
    call_hours_perc: number
}

export async function getDailyCalls(year: number, nDays: number = 30): Promise<DailyCallCount[]> {
    try {
        const {data} = await http.get<DailyCallCount[]>('/api/statistics/daily_calls', {params: {year, n_days: nDays}})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to load daily call statistics.'})
        throw e
    }
}

export async function getMemberDailyCalls(year: number, nDays: number = 30, member?: string): Promise<MemberDailyStats[]> {
    try {
        const params: any = {year, n_days: nDays}
        if (member) params.member = member
        const {data} = await http.get<MemberDailyStats[]>('/api/statistics/member_daily_calls', {params})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to load member daily statistics.'})
        throw e
    }
}

export async function getCallGroups(year: number): Promise<CallGroupCount[]> {
    try {
        const {data} = await http.get<CallGroupCount[]>('/api/statistics/call_groups', {params: {year}})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to load call group statistics.'})
        throw e
    }
}

export async function getCallGroupsMonthly(year: number): Promise<CallGroupMonthCount[]> {
    try {
        const {data} = await http.get<CallGroupMonthCount[]>('/api/statistics/call_groups_monthly', {params: {year}})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to load monthly call group statistics.'})
        throw e
    }
}

export async function getYearSummary(year: number): Promise<YearSummary | null> {
    try {
        const {data} = await http.get<YearSummary | null>('/api/statistics/year_summary', {params: {year}})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to load year summary.'})
        throw e
    }
}

export async function getMemberYearStats(year: number): Promise<MemberYearStats[]> {
    try {
        const {data} = await http.get<MemberYearStats[]>('/api/statistics/member_year_stats', {params: {year}})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to load member year statistics.'})
        throw e
    }
}

export interface MemberCallEntry {
    call_id: number
    start: string
    end: string
    subjects: string
}

export async function getMemberCalls(memberId: number, year?: number): Promise<MemberCallEntry[]> {
    try {
        const params: any = {member_id: memberId}
        if (year) params.year = year
        const {data} = await http.get<MemberCallEntry[]>(`/api/statistics/member_calls/${memberId}`, {params: year ? {year} : {}})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to load member call history.'})
        throw e
    }
}
