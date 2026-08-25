import {getHttpClient} from "./http.ts";
import {emitError} from "../events/bus.ts";
import type {Exercise, FullExercise} from "../interfaces/Exercise.ts";
import type {Page} from "../interfaces/Page.ts";

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

export async function listExercises(page: number = 1, pageSize: number = 100): Promise<Page<FullExercise>> {
    try {
        const {data} = await http.get<Page<FullExercise>>('/api/exercises', {params: {page, size: pageSize}})
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to list exercises.'})
        throw e
    }
}

export async function addExerciseMembers(exercise: Exercise, members: Number[]): Promise<void> {
    try {
        await http.put<void>(`/api/exercise/${exercise.id}/member`, members)
    } catch (e) {
        emitError(e, {message: 'Failed to add exercise members.'})
        throw e
    }
}