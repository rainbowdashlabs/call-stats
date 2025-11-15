export function parseTime(date: string, time: string): number {
    return Math.floor(new Date(`${date}T${time}:00`).getTime() / 1000)
}

export function parseDate(date: string) {
    return Math.floor(new Date(date).getTime() / 1000)
}
