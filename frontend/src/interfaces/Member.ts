export interface Member extends SimpleMember{
    retired: number | null | string
    usage?: number
}

export interface SimpleMember  {
    id?: number
    name: string
}