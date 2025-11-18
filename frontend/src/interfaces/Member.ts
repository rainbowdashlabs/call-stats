export interface Member extends SimpleMember{
    retired: number | null | string
}

export interface SimpleMember  {
    id?: number
    name: string
}