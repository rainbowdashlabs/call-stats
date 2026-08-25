import type {FullCall} from "../interfaces/Call.ts";
import {emitError} from "../events/bus.ts";
import {getHttpClient} from "./http.ts";
import {t} from '../i18n'

const http = getHttpClient()

export async function getCall(id: number): Promise<FullCall> {
    try {
        const {data} = await http.get<FullCall>(`/api/call/${id}`)
        return data
    } catch (e) {
        emitError(e, {message: t('errors.callLoad')})
        throw e
    }
}

export async function updateCall(call: {id: number, start: number | string, end: number | string, additional: number, note?: string | null, abort_reason?: string | null}): Promise<void> {
    try {
        await http.patch('/api/call', call)
    } catch (e) {
        emitError(e, {message: t('errors.callUpdate')})
        throw e
    }
}

export async function removeCall(id: number): Promise<void> {
    try {
        await http.delete<FullCall>(`/api/call/${id}`)
    } catch (e) {
        emitError(e, {message: t('errors.callDelete')})
        throw e
    }
}