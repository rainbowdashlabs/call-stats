import type {MultiSelectGroup, Subject} from '../interfaces/Subject'
import {getHttpClient} from './http'

const http = getHttpClient()

export async function listSubjects(): Promise<MultiSelectGroup[]> {
    const {data} = await http.get<MultiSelectGroup[]>('/api/subjects?grouped=true')
    return data
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
