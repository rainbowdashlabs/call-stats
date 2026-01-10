import {getHttpClient} from './http'
import type {Member} from "../interfaces/Member.ts";
import {emitError} from '../events/bus'

const http = getHttpClient()

export async function listMembers(active: boolean = false, active_after: number | null = null): Promise<Member[]> {
    try {
        const {data} = await http.get<Member[]>('/api/members', {params: {filter_active: active, active_after: active_after}})
        return data
    } catch (e) {
        emitError(e, { message: 'Failed to load members.' })
        throw e
    }
}

export async function createMember(member: Member): Promise<Member> {
    try {
        const {data} = await http.post<Member>('/api/members', member)
        return data
    } catch (e) {
        emitError(e, { message: 'Failed to create member.' })
        throw e
    }
}