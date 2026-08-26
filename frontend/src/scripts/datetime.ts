export function parseTime(date: string, time: string): number {
    return Math.floor(new Date(`${date}T${time}:00`).getTime() / 1000)
}

export function parseDate(date: string) {
    return Math.floor(new Date(date).getTime() / 1000)
}

export function todayDate(): string {
    return new Date().toISOString().split('T')[0]!
}

export function today(): string {
    return new Date().toISOString()
}

export function formatDateTime(date: string): string {
    return new Date(date).toLocaleString('de-DE')
}

/** Day and time without the year, short enough for an axis label. */
export function formatDayTime(date: string): string {
    return new Date(date).toLocaleString('de-DE', {day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'})
}

/**
 * Formats a date that the API may deliver either way: dates are sent as unix timestamps but
 * come back as ISO strings, because the backend's `EpochDate` only converts on the way in.
 */
export function formatDate(value: number | string): string {
    const date = typeof value === 'number' ? new Date(value * 1000) : new Date(value)
    return date.toLocaleDateString('de-DE')
}

/** Renders a span of minutes as h:mm, the way a duty log writes it. */
export function formatDuration(minutes: number): string {
    const whole = Math.max(0, Math.round(minutes))
    return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, '0')}`
}

/**
 * Where a call sits on a 24-hour track: how far into the day it starts and how much of the
 * day it covers, both as percentages, clamped so a call running past midnight ends at 24:00.
 */
export function dayPosition(start: string | number, end: string | number): { left: number, width: number } {
    const from = typeof start === 'number' ? new Date(start * 1000) : new Date(start)
    const to = typeof end === 'number' ? new Date(end * 1000) : new Date(end)
    const startMinute = from.getHours() * 60 + from.getMinutes()
    const minutes = Math.max(1, (to.getTime() - from.getTime()) / 60000)
    return {
        left: (startMinute / 1440) * 100,
        width: (Math.min(minutes, 1440 - startMinute) / 1440) * 100
    }
}

export function getDaysInMonth(year: number, month: number): number {
    return new Date(year, month, 0).getDate();
}

export function getCurrentYear(): number {
    return new Date().getFullYear()
}

export function getCurrentMonth(): number {
    return new Date().getMonth() + 1
}

export function getCurrentDay(): number {
    return new Date().getDate()
}

export function getCurrentHour(): number {
    return new Date().getHours()
}

export function getCurrentMinute(): number {
    return new Date().getMinutes()
}

export function getCurrentSecond(): number {
    return new Date().getSeconds()
}

export interface ATime {
    hour: number;
    minute: number;
    second: number;
}

export interface ADate {
    year: number;
    month: number;
    day: number;
}

export class ADateTime implements ATime, ADate{
    year: number;
    month: number;
    day: number;
    hour: number;
    minute: number;
    second: number;

    constructor(year: number, month: number, day: number, hour: number, minute: number, second: number) {
        this.year = year;
        this.month = month;
        this.day = day;
        this.hour = hour;
        this.minute = minute;
        this.second = second;
    }

    static now(): ADateTime {
        return this.fromDate(new Date())
    }

    static fromDate(date: Date): ADateTime {
        return new ADateTime(date.getFullYear(), date.getMonth() + 1, date.getDate(), date.getHours(), date.getMinutes(), date.getSeconds())
    }

    toString(): string {
        return `${this.year}-${this.month}-${this.day} ${this.hour}:${this.minute}:${this.second}`
    }

    toDate(): Date {
        return new Date(this.year, this.month - 1, this.day, this.hour, this.minute, this.second)
    }

    public applyDate(date: ADate): ADateTime {
        return new ADateTime(date.year, date.month, date.day, this.hour, this.minute, this.second)
    }

    public nextDay(): ADateTime {
        return this.addDays(1)
    }

    public addMinutes(minutes: number): ADateTime {
        const date = this.toDate()
        date.setMinutes(date.getMinutes() + minutes)
        return ADateTime.fromDate(date)
    }

    public addDays(days: number): ADateTime {
        const date = this.toDate()
        date.setDate(date.getDate() + days)
        return ADateTime.fromDate(date)
    }

    public withoutTime(): ADateTime {
        return new ADateTime(this.year, this.month, this.day, 0, 0, 0)
    }

    public toUnixTimestamp(): number {
        return Math.floor(this.toDate().getTime() / 1000)
    }
}