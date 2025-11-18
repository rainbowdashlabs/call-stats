import type {FullCall} from "../interfaces/Call.ts";
import {emitError} from "../events/bus.ts";
import {getHttpClient} from "./http.ts";

const http = getHttpClient()

export async function getCall(id: number): Promise<FullCall> {
    try {
        const {data} = await http.get<FullCall>(`/api/call/${id}`)
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to load calls.'})
        throw e
    }
}

export async function removeCall(id: number): Promise<void> {
    try {
        await http.delete<FullCall>(`/api/call/${id}`)
    } catch (e) {
        emitError(e, {message: 'Failed to load calls.'})
        throw e
    }
}