import {getHttpClient} from "./http.ts";
import {emitError} from "../events/bus.ts";
import type {Exercise} from "../interfaces/Exercise.ts";
import type {FullYouthExercise, YouthExercise} from "../interfaces/YouthExercise.ts";
import type {Page} from "../interfaces/Page.ts";
import {t} from '../i18n'

const http = getHttpClient()

export async function createYouthExercise(exercise: YouthExercise): Promise<YouthExercise> {
    try {
        const {data} = await http.post<YouthExercise>('/api/youth_exercises', exercise)
        return data
    } catch (e) {
        emitError(e, {message: t('errors.youthExerciseCreate')})
        throw e
    }
}

export async function listYouthExercises(page: number = 1, pageSize: number = 100): Promise<Page<FullYouthExercise>> {
    try {
        const {data} = await http.get<Page<FullYouthExercise>>('/api/youth_exercises', {params: {page, per_page: pageSize}})
        return data
    } catch (e) {
        emitError(e, {message: t('errors.youthExercisesLoad')})
        throw e
    }
}

export async function addYouthExerciseMembers(exercise: Exercise, members: Number[]): Promise<void> {
    try {
        await http.put<void>(`/api/youth_exercise/${exercise.id}/member`, members)
    } catch (e) {
        emitError(e, {message: t('errors.youthExerciseMembersAdd')})
        throw e
    }
}