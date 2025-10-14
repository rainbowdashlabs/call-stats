import {getHttpClient} from './http'
import type {CreateCall} from "../interfaces/CreateCall.ts";

const http = getHttpClient()

export async function createCall(call: CreateCall) {
    await http.post<CreateCall>('/api/calls', call)
}
