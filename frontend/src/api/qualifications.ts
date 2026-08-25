import {getHttpClient} from './http'
import type {Qualification} from "../interfaces/Qualification.ts";
import {emitError} from '../events/bus'
import {t} from '../i18n'

const http = getHttpClient()

export async function listQualifications() {
    try {
        const {data} = await http.get<Qualification[]>('/api/qualifications')
        return data
    } catch (e) {
        emitError(e, { message: t('errors.qualificationsLoad') })
        throw e
    }
}

export async function createQualification(qualification: Qualification) {
    try {
        const {data} = await http.post<Qualification>('/api/qualifications', qualification)
        return data
    } catch (e) {
        emitError(e, { message: t('errors.qualificationCreate') })
        throw e
    }
}

export async function searchQualification(name: string) {
    try {
        const {data} = await http.get<Qualification[]>('/api/qualifications', {params: {name: name}})
        return data
    } catch (e) {
        emitError(e, { message: t('errors.qualificationsSearch') })
        throw e
    }
}