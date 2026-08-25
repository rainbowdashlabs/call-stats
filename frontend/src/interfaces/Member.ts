export interface Member extends SimpleMember{
    joined?: number | null | string
    retired: number | null | string
    usage?: number
}

export interface SimpleMember  {
    id?: number
    name: string
}