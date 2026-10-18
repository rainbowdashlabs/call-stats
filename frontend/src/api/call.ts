import type {FullCall, UpdateCall} from "../interfaces/Call.ts";
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

export async function updateCall(call: UpdateCall): Promise<FullCall> {
    try {
        const {data} = await http.patch<FullCall>('/api/call', call)
        return data
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