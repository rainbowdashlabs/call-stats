import {getHttpClient} from "./http.ts";
import {emitError} from "../events/bus.ts";
import type {Exercise} from "../interfaces/Exercise.ts";
import type {FullYouthExercise, YouthExercise} from "../interfaces/YouthExercise.ts";

const http = getHttpClient()

export async function createYouthExercise(exercise: YouthExercise): Promise<YouthExercise> {
    try {
        const {data} = await http.post<YouthExercise>('/api/youth_exercises', exercise)
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to create exercise.'})
        throw e
    }
}

export async function listYouthExercises(page: number = 1, pageSize: number = 100): Promise<FullYouthExercise> {
    try {
        const {data} = await http.post<FullYouthExercise>('/api/youth_exercises', {query: {page: page, size: pageSize}})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to create exercise.'})
        throw e
    }
}

export async function addYouthExerciseMembers(exercise: Exercise, members: Number[]): Promise<void> {
    try {
        await http.put<void>(`/api/youth_exercise/${exercise.id}/member`, members)
    } catch (e) {
        emitError(e, {message: 'Failed to create exercise.'})
        throw e
    }
}