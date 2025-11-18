export interface Page<T> {
    page: number,
    size: number,
    pages: number,
    entries: T[]
}