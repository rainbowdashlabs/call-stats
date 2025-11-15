import {getHttpClient} from './http'
import type {Qualification} from "../interfaces/Qualification.ts";

const http = getHttpClient()

export async function getQualification(id: number): Promise<Qualification> {
    const {data} = await http.get<Qualification>(`/api/qualification/${id}`)
    return data
}

export async function updateQualification(qualification: Qualification): Promise<Qualification> {
    const {data} = await http.patch<Qualification>(`/api/qualification/${qualification.id}`, qualification)
    return data
}

export async function deleteQualification(id: number): Promise<void> {
    await http.delete(`/api/qualification/${id}`)
}