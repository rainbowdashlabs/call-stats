export interface Qualification {
    id?: number
    name: string
}

export interface MemberQualification {
    member_id: number,
    qualification_id: number,
    since: number
}