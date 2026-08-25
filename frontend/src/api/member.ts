import {getHttpClient} from './http'
import type {Member} from "../interfaces/Member.ts";
import type {MemberQualification} from "../interfaces/Qualification.ts";
import {emitError} from '../events/bus'
import {t} from '../i18n'

const http = getHttpClient()

export async function getMember(id: number): Promise<Member> {
    try {
        const {data} = await http.get<Member>(`/api/member/${id}`)
        return data
    } catch (e) {
        emitError(e, { message: t('errors.memberLoad') })
        throw e
    }
}

export async function deleteMember(id: number): Promise<void> {
    try {
        await http.delete(`/api/member/${id}`)
    } catch (e) {
        emitError(e, { message: t('errors.memberDelete') })
        throw e
    }
}

export async function updateMember(member: Member): Promise<Member> {
    try {
        const {data} = await http.put<Member>(`/api/member/${member.id!}`, member)
        return data
    } catch (e) {
        emitError(e, { message: t('errors.memberUpdate') })
        throw e
    }
}

export async function addQualification(qualification: MemberQualification): Promise<MemberQualification> {
    try {
        const {data} = await http.post(`/api/member/${qualification.member_id}/qualification`, qualification)
        return data
    } catch (e) {
        emitError(e, { message: t('errors.qualificationAdd') })
        throw e
    }
}

export async function getQualifications(member: Member): Promise<MemberQualification[]> {
    try {
        const {data} = await http.get<MemberQualification[]>(`/api/member/${member.id}/qualifications`)
        return data
    } catch (e) {
        emitError(e, { message: t('errors.qualificationsLoad') })
        throw e
    }
}

export async function removeQualification(qualification: MemberQualification): Promise<void> {
    try {
        await http.delete(`/api/member/${qualification.member_id}/qualification/${qualification.qualification_id}`)
    } catch (e) {
        emitError(e, { message: t('errors.qualificationRemove') })
        throw e
    }
}

export async function addCall(member: Member, call_id: number): Promise<void> {
    try {
        await http.post(`/api/member/${member.id}/call/${call_id}`)
    } catch (e) {
        emitError(e, { message: t('errors.memberCallAdd') })
        throw e
    }
}

export async function removeCall(member: Member, call_id: number): Promise<void> {
    try {
        await http.delete(`/api/member/${member.id}/call/${call_id}`)
    } catch (e) {
        emitError(e, { message: t('errors.memberCallRemove') })
        throw e
    }
}

export async function addExercise(member: Member, exercise_id: number): Promise<void> {
    try {
        await http.post(`/api/member/${member.id}/exercise/${exercise_id}`)
    } catch (e) {
        emitError(e, { message: t('errors.memberExerciseAdd') })
        throw e
    }
}

export async function removeExercise(member: Member, exercise_id: number): Promise<void> {
    try {
        await http.delete(`/api/member/${member.id}/exercise/${exercise_id}`)
    } catch (e) {
        emitError(e, { message: t('errors.memberExerciseRemove') })
        throw e
    }
}

export async function addYouthExercise(member: Member, youth_exercise_id: number): Promise<void> {
    try {
        await http.post(`/api/member/${member.id}/youth_exercise/${youth_exercise_id}`)
    } catch (e) {
        emitError(e, { message: t('errors.memberYouthExerciseAdd') })
        throw e
    }
}

export async function removeYouthExercise(member: Member, youth_exercise_id: number): Promise<void> {
    try {
        await http.delete(`/api/member/${member.id}/youth_exercise/${youth_exercise_id}`)
    } catch (e) {
        emitError(e, { message: t('errors.memberYouthExerciseRemove') })
        throw e
    }
}