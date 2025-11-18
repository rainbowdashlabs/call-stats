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
    return new Date(date).toLocaleString()
}