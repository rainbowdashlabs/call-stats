import {getHttpClient} from "./http.ts";
import {emitError} from "../events/bus.ts";
import type {Exercise} from "../interfaces/Exercise.ts";

const http = getHttpClient()

export async function createExercise(exercise: Exercise): Promise<Exercise> {
    try {
        const {data} = await http.post<Exercise>('/api/exercises', exercise)
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to create exercise.'})
        throw e
    }
}

export async function listExercises(page: number = 1, pageSize: number = 100): Promise<Exercise> {
    try {
        const {data} = await http.post<Exercise>('/api/exercises', {query: {page: page, size: pageSize}})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to create exercise.'})
        throw e
    }
}

