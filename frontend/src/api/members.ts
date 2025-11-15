import {getHttpClient} from './http'
import type {Member} from "../interfaces/Member.ts";

const http = getHttpClient()

export async function listMembers(active: boolean = false): Promise<Member[]> {
    const {data} = await http.get<Member[]>('/api/members', {params: {active: active}})
    return data
}

export async function createMember(member: Member): Promise<Member> {
    const {data} = await http.post<Member>('/api/members', member)
    return data
}