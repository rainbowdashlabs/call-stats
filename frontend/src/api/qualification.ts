import {getHttpClient} from './http'
import type {Qualification} from "../interfaces/Qualification.ts";
import {emitError} from '../events/bus'

const http = getHttpClient()

export async function getQualification(id: number): Promise<Qualification> {
    try {
        const {data} = await http.get<Qualification>(`/api/qualification/${id}`)
        return data
    } catch (e) {
        emitError(e, { message: 'Failed to load qualification.' })
        throw e
    }
}

export async function updateQualification(qualification: Qualification): Promise<Qualification> {
    try {
        const {data} = await http.patch<Qualification>(`/api/qualification/${qualification.id}`, qualification)
        return data
    } catch (e) {
        emitError(e, { message: 'Failed to update qualification.' })
        throw e
    }
}

export async function deleteQualification(id: number): Promise<void> {
    try {
        await http.delete(`/api/qualification/${id}`)
    } catch (e) {
        emitError(e, { message: 'Failed to delete qualification.' })
        throw e
    }
}