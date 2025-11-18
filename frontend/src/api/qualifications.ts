import {getHttpClient} from './http'
import type {Qualification} from "../interfaces/Qualification.ts";
import {emitError} from '../events/bus'

const http = getHttpClient()

export async function listQualifications() {
    try {
        const {data} = await http.get<Qualification[]>('/api/qualifications')
        return data
    } catch (e) {
        emitError(e, { message: 'Failed to load qualifications.' })
        throw e
    }
}

export async function createQualification(qualification: Qualification) {
    try {
        const {data} = await http.post<Qualification>('/api/qualifications', qualification)
        return data
    } catch (e) {
        emitError(e, { message: 'Failed to create qualification.' })
        throw e
    }
}

export async function searchQualification(name: string) {
    try {
        const {data} = await http.get<Qualification[]>('/api/qualifications', {params: {name: name}})
        return data
    } catch (e) {
        emitError(e, { message: 'Failed to search qualifications.' })
        throw e
    }
}