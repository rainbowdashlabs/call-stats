import {getHttpClient} from "./http.ts";
import type {Exercise, FullExercise} from "../interfaces/Exercise.ts";
import {emitError} from "../events/bus.ts";
import type {Member} from "../interfaces/Member.ts";

const http = getHttpClient()

export async function deleteExercise(exercise: Exercise): Promise<void> {
    try {
        await http.delete<Exercise>(`/api/exercise/${exercise.id!}`,)
    } catch (e) {
        emitError(e, {message: 'Failed to delete exercise.'})
        throw e
    }
}

export async function getExercise(exercise: number): Promise<FullExercise> {
    try {
        const {data} = await http.get<FullExercise>(`/api/exercise/${exercise!}`,)
        return data
    } catch (e) {
        emitError(e, {message: 'Failed to retrieve exercise.'})
        throw e
    }
}

export async function deleteExerciseMember(exercise: Exercise, members: Member[]): Promise<void> {
    try {
        await http.delete<Exercise>(`/api/exercise/${exercise.id!}/member`, {data: members.map(m => m.id!)})
    } catch (e) {
        emitError(e, {message: 'Failed to delete exercise.'})
        throw e
    }
}

export async function addExerciseMember(exercise: Exercise, members: Member[]): Promise<void> {
    try {
        await http.put<Exercise>(`/api/exercise/${exercise.id!}/member`, {data: members.map(m => m.id!)})
    } catch (e) {
        emitError(e, {message: 'Failed to modify exercise.'})
        throw e
    }
}
