import {getHttpClient} from "./http.ts";
import {emitError} from "../events/bus.ts";
import {t} from '../i18n'

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
        emitError(e, {message: t('errors.statisticsDailyCalls')})
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
        emitError(e, {message: t('errors.statisticsMemberDailyCalls')})
        throw e
    }
}

export async function getCallGroups(year: number): Promise<CallGroupCount[]> {
    try {
        const {data} = await http.get<CallGroupCount[]>('/api/statistics/call_groups', {params: {year}})
        return data
    } catch (e) {
        emitError(e, {message: t('errors.statisticsCallGroups')})
        throw e
    }
}

export async function getCallGroupsMonthly(year: number): Promise<CallGroupMonthCount[]> {
    try {
        const {data} = await http.get<CallGroupMonthCount[]>('/api/statistics/call_groups_monthly', {params: {year}})
        return data
    } catch (e) {
        emitError(e, {message: t('errors.statisticsCallGroupsMonthly')})
        throw e
    }
}

export async function getYearSummary(year: number): Promise<YearSummary | null> {
    try {
        const {data} = await http.get<YearSummary | null>('/api/statistics/year_summary', {params: {year}})
        return data
    } catch (e) {
        emitError(e, {message: t('errors.statisticsYearSummary')})
        throw e
    }
}

export async function getMemberYearStats(year: number): Promise<MemberYearStats[]> {
    try {
        const {data} = await http.get<MemberYearStats[]>('/api/statistics/member_year_stats', {params: {year}})
        return data
    } catch (e) {
        emitError(e, {message: t('errors.statisticsMemberYearStats')})
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
        emitError(e, {message: t('errors.statisticsMemberCalls')})
        throw e
    }
}

export interface YearRange {
    min_year: number
    max_year: number
}

export interface YearlySeriesEntry {
    year: number
    call_count: number
    call_hours: number
    crew_hours: number
    aborted: number
    avg_crew: number
    exercise_count: number
    exercise_hours: number
    exercise_attendance: number
    youth_count: number
    youth_hours: number
    youth_participants: number
    roster_members: number
    participating_members: number
}

export interface CallTimeProfileEntry {
    weekday: number
    hour: number
    call_count: number
}

export interface CallSubjectCount {
    name: string
    group: string
    call_count: number
}

export interface AbortReasonCount {
    reason: string
    call_count: number
}

export interface DurationBucket {
    bucket: string
    call_count: number
}

export interface LongestCall {
    call_id: number
    start: string
    minutes: number
    crew: number
    subjects: string
}

export interface QualificationCoverage {
    call_count: number
    with_leader: number
    with_driver: number
    with_both: number
}

export interface TurnoutBucket {
    bucket: string
    member_count: number
}

export interface ExerciseSummary {
    exercise_count: number
    exercise_hours: number
    attendance: number
    avg_attendance: number
    crew_hours: number
}

export interface ExerciseSession {
    exercise_id: number
    exercise_date: string
    subject: string
    minutes: number
    attendance: number
}

export interface ExerciseMemberStats {
    member_id: number
    member_name: string
    attended: number
    exercise_hours: number
    attended_perc: number
}

export interface YouthSummary {
    session_count: number
    session_hours: number
    participants: number
    avg_participants: number
    instructor_count: number
    instructor_hours: number
}

export interface YouthSession {
    exercise_id: number
    exercise_date: string
    subject: string
    minutes: number
    participants: number
    instructors: number
}

export interface CombinedMemberStats {
    member_id: number
    member_name: string
    call_count: number
    call_hours: number
    exercise_count: number
    exercise_hours: number
    youth_count: number
    youth_hours: number
    total_hours: number
}

export interface MembershipEntry {
    year: number
    roster_members: number
    retired_in_year: number
    participating_members: number
}

export interface MemberYearTrendEntry {
    year: number
    call_count: number
    call_hours: number
    call_count_perc: number
    exercise_count: number
    youth_count: number
}

export interface PresentationData {
    year: number
    call_summary: YearSummary | null
    call_groups: CallGroupCount[]
    call_groups_monthly: CallGroupMonthCount[]
    call_subjects: CallSubjectCount[]
    call_time_profile: CallTimeProfileEntry[]
    call_durations: DurationBucket[]
    qualification_coverage: QualificationCoverage
    exercise_summary: ExerciseSummary
    exercise_sessions: ExerciseSession[]
    exercise_member_stats: ExerciseMemberStats[]
    youth_summary: YouthSummary
    youth_sessions: YouthSession[]
    combined_member_stats: CombinedMemberStats[]
    turnout_distribution: TurnoutBucket[]
    membership: MembershipEntry[]
    yearly_series: YearlySeriesEntry[]
}

async function fetchStatistics<T>(path: string, params: object, errorKey: string): Promise<T> {
    try {
        const {data} = await http.get<T>(`/api/statistics/${path}`, {params})
        return data
    } catch (e) {
        emitError(e, {message: t(errorKey)})
        throw e
    }
}

export function getYearRange(): Promise<YearRange> {
    return fetchStatistics('year_range', {}, 'errors.statisticsYearRange')
}

export function getYearlySeries(year: number, yearsBack: number = 5): Promise<YearlySeriesEntry[]> {
    return fetchStatistics('yearly_series', {year, years_back: yearsBack}, 'errors.statisticsYearlySeries')
}

export function getCallTimeProfile(year: number): Promise<CallTimeProfileEntry[]> {
    return fetchStatistics('call_time_profile', {year}, 'errors.statisticsTimeProfile')
}

export function getCallSubjects(year: number, limit: number = 10): Promise<CallSubjectCount[]> {
    return fetchStatistics('call_subjects', {year, limit}, 'errors.statisticsCallSubjects')
}

export function getAbortReasons(year: number): Promise<AbortReasonCount[]> {
    return fetchStatistics('abort_reasons', {year}, 'errors.statisticsAbortReasons')
}

export function getCallDurations(year: number): Promise<DurationBucket[]> {
    return fetchStatistics('call_durations', {year}, 'errors.statisticsCallDurations')
}

export function getLongestCalls(year: number, limit: number = 5): Promise<LongestCall[]> {
    return fetchStatistics('longest_calls', {year, limit}, 'errors.statisticsLongestCalls')
}

export function getQualificationCoverage(year: number): Promise<QualificationCoverage> {
    return fetchStatistics('qualification_coverage', {year}, 'errors.statisticsQualificationCoverage')
}

export function getTurnoutDistribution(year: number): Promise<TurnoutBucket[]> {
    return fetchStatistics('turnout_distribution', {year}, 'errors.statisticsTurnout')
}

export function getExerciseSummary(year: number): Promise<ExerciseSummary> {
    return fetchStatistics('exercise_summary', {year}, 'errors.statisticsExercises')
}

export function getExerciseSessions(year: number): Promise<ExerciseSession[]> {
    return fetchStatistics('exercise_sessions', {year}, 'errors.statisticsExercises')
}

export function getExerciseMemberStats(year: number): Promise<ExerciseMemberStats[]> {
    return fetchStatistics('exercise_member_stats', {year}, 'errors.statisticsExercises')
}

export function getYouthSummary(year: number): Promise<YouthSummary> {
    return fetchStatistics('youth_summary', {year}, 'errors.statisticsYouth')
}

export function getYouthSessions(year: number): Promise<YouthSession[]> {
    return fetchStatistics('youth_sessions', {year}, 'errors.statisticsYouth')
}

export function getCombinedMemberStats(year: number): Promise<CombinedMemberStats[]> {
    return fetchStatistics('combined_member_stats', {year}, 'errors.statisticsCombined')
}

export function getMembership(year: number, yearsBack: number = 5): Promise<MembershipEntry[]> {
    return fetchStatistics('membership', {year, years_back: yearsBack}, 'errors.statisticsMembership')
}

export function getMemberYearTrend(memberId: number, year: number, yearsBack: number = 5): Promise<MemberYearTrendEntry[]> {
    return fetchStatistics(`member_year_trend/${memberId}`, {year, years_back: yearsBack}, 'errors.statisticsMemberTrend')
}

export interface MemberYearSummary extends MemberYearStats {
    rank: number
    member_count: number
}

export function getMemberYearSummary(year: number, member: string): Promise<MemberYearSummary | null> {
    return fetchStatistics('member_year_summary', {year, member}, 'errors.statisticsMemberYearStats')
}

export function getPresentation(year: number, yearsBack: number = 5): Promise<PresentationData> {
    return fetchStatistics('presentation', {year, years_back: yearsBack}, 'errors.statisticsPresentation')
}
