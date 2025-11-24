import {getHttpClient} from './http'
import type {CreateCall, FullCall} from "../interfaces/Call.ts";
import {emitError} from '../events/bus'
import type {Page} from "../interfaces/Page.ts";

const http = getHttpClient()

export async function createCall(call: CreateCall) {
    try {
        await http.post<CreateCall>('/api/calls', call)
    } catch (e) {
        emitError(e, {message: `Failed to create call. ${JSON.stringify(call)}`})
        throw e
    }
}

export async function listCalls(page: number = 1, per_page: number = 20) {
    try {
        const {data} = await http.get<Page<FullCall>>('/api/calls', {params: {page: page, per_page: per_page}})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to load calls.'})
        throw e
    }
}

export async function listAbortReasons(): Promise<String[]> {
    try {
        const {data} = await http.get<String[]>('/api/calls/abort_reasons')
        return data
    } catch (e) {
        emitError(e, { message: 'Failed to retrieve abort reasons.' })
        throw e
    }
}