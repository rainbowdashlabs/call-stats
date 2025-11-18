import type {MultiSelectGroup, Subject} from '../interfaces/Subject'
import {getHttpClient} from './http'
import {emitError} from '../events/bus'

const http = getHttpClient()

export async function listSubjects(grouped: boolean = true): Promise<MultiSelectGroup[] | Subject[]> {
    try {
        if (grouped) {
            const {data} = await http.get<MultiSelectGroup[]>('/api/subjects', {params: {grouped: grouped}})
            return data
        } else {
            const {data} = await http.get<Subject[]>('/api/subjects', {params: {grouped: grouped}})
            return data
        }
    } catch (e) {
        emitError(e, { message: 'Failed to load subjects.' })
        throw e
    }
}

export async function createSubject(subject: Subject): Promise<Subject> {
    try {
        const {data} = await http.post<Subject>('/api/subjects', subject)
        return data
    } catch (e) {
        emitError(e, { message: 'Failed to create subject.' })
        throw e
    }
}

export async function updateSubject(id: number, subject: Subject): Promise<Subject> {
    try {
        const {data} = await http.patch<Subject>(`/api/subject/${id}`, subject)
        return data
    } catch (e) {
        emitError(e, { message: 'Failed to update subject.' })
        throw e
    }
}

export async function deleteSubject(id: number): Promise<void> {
    try {
        await http.delete(`/api/subject/${id}`)
    } catch (e) {
        emitError(e, { message: 'Failed to delete subject.' })
        throw e
    }
}
