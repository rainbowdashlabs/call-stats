export interface CreateCall {
    subjects: number[]
    start: number
    end: number
    abort_reason?: string | null
    note?: string | null
    members: number[]
}