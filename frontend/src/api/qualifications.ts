import {getHttpClient} from './http'
import type {Qualification} from "../interfaces/Qualification.ts";

const http = getHttpClient()

export async function listQualifications() {
    const {data} = await http.get<Qualification[]>('/api/qualifications')
    return data
}

export async function createQualification(qualification: Qualification) {
    const {data} = await http.post<Qualification>('/api/qualifications', qualification)
    return data
}

export async function searchQualification(name: string) {
    const {data} = await http.get<Qualification[]>('/api/qualifications', {params: {name: name}})
    return data
}