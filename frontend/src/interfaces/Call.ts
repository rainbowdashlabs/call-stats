import type {SimpleSubject} from "./Subject.ts";
import type {SimpleMember} from "./Member.ts";

export interface CreateCall {
    subjects: number[]
    start: number
    end: number
    additional: number
    abort_reason?: string | null
    note?: string | null
    members: number[]
}


export interface FullCall {
    id: number
    subjects: SimpleSubject[]
    start: number|string
    end: number|string
    additional: number
    abort_reason?: string | null
    note?: string | null
    members: SimpleMember[]
}