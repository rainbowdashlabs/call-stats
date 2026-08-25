import {getHttpClient} from './http'
import type {Qualification} from "../interfaces/Qualification.ts";
import {emitError} from '../events/bus'
import {t} from '../i18n'

const http = getHttpClient()

export async function getQualification(id: number): Promise<Qualification> {
    try {
        const {data} = await http.get<Qualification>(`/api/qualification/${id}`)
        return data
    } catch (e) {
        emitError(e, { message: t('errors.qualificationLoad') })
        throw e
    }
}

export async function updateQualification(qualification: Qualification): Promise<Qualification> {
    try {
        const {data} = await http.patch<Qualification>(`/api/qualification/${qualification.id}`, qualification)
        return data
    } catch (e) {
        emitError(e, { message: t('errors.qualificationUpdate') })
        throw e
    }
}

export async function deleteQualification(id: number): Promise<void> {
    try {
        await http.delete(`/api/qualification/${id}`)
    } catch (e) {
        emitError(e, { message: t('errors.qualificationDelete') })
        throw e
    }
}