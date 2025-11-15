import {getHttpClient} from './http'
import type {Member} from "../interfaces/Member.ts";
import type {MemberQualification} from "../interfaces/Qualification.ts";

const http = getHttpClient()

export async function getMember(id: number): Promise<Member> {
    const {data} = await http.get<Member>(`/api/member/${id}`)
    return data
}

export async function deleteMember(id: number): Promise<void> {
    await http.delete(`/api/member/${id}`)
}

export async function updateMember(member: Member): Promise<Member> {
    const {data} = await http.put<Member>(`/api/member/${member.id!}`, member)
    return data
}

export async function addQualification(qualification: MemberQualification): Promise<void> {
    await http.post(`/api/member/${qualification.member_id}/qualification`, qualification)
}

export async function getQualifications(member: Member): Promise<MemberQualification[]> {
    const {data} = await http.get<MemberQualification[]>(`/api/member/${member.id}/qualifications`)
    return data
}

export async function removeQualification(qualification: MemberQualification): Promise<void> {
    await http.delete(`/api/member/${qualification.member_id}/qualification/${qualification.qualification_id}`)
}

export async function addCall(member: Member, call_id: number): Promise<void> {
    await http.post(`/api/member/${member.id}/call/${call_id}`)
}

export async function removeCall(member: Member, call_id: number): Promise<void> {
    await http.delete(`/api/member/${member.id}/call/${call_id}`)
}

export async function addExercise(member: Member, exercise_id: number): Promise<void> {
    await http.post(`/api/member/${member.id}/exercise/${exercise_id}`)
}

export async function removeExercise(member: Member, exercise_id: number): Promise<void> {
    await http.delete(`/api/member/${member.id}/exercise/${exercise_id}`)
}

export async function addYouthExercise(member: Member, youth_exercise_id: number): Promise<void> {
    await http.post(`/api/member/${member.id}/youth_exercise/${youth_exercise_id}`)
}

export async function removeYouthExercise(member: Member, youth_exercise_id: number): Promise<void> {
    await http.delete(`/api/member/${member.id}/youth_exercise/${youth_exercise_id}`)
}