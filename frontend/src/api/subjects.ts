import type {MultiSelectGroup, Subject} from '../interfaces/Subject'
import {getHttpClient} from './http'

const http = getHttpClient()

export async function listSubjects(grouped: boolean = true): Promise<MultiSelectGroup[] | Subject[]> {
    if (grouped) {
        const {data} = await http.get<Subject[]>('/api/subjects', {params: {grouped: grouped}})
        return data
    } else {
        const {data} = await http.get<MultiSelectGroup[]>('/api/subjects', {params: {grouped: grouped}})
        return data
    }
}

export async function createSubject(subject: Subject): Promise<Subject> {
    const {data} = await http.post<Subject>('/api/subjects', subject)
    return data
}

export async function updateSubject(id: number, subject: Subject): Promise<Subject> {
    const {data} = await http.patch<Subject>(`/api/subject/${id}`, subject)
    return data
}

export async function deleteSubject(id: number): Promise<void> {
    await http.delete(`/api/subject/${id}`)
}
