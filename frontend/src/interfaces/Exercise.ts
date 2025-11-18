import type {SimpleMember} from "./Member.ts";

export interface Exercise {
    id?: number,
    subject: string,
    exercise_date: number,
    duration: number
}

export interface FullExercise extends Exercise {
    members: SimpleMember
}