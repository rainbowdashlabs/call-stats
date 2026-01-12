import type {SimpleMember} from "./Member.ts";

export interface YouthExercise {
    id?: number,
    subject: string,
    exercise_date: number,
    duration: number,
    participants: number
}

export interface FullYouthExercise extends YouthExercise {
    instructors: SimpleMember
}