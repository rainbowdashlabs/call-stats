export interface Subject extends SimpleSubject {
    archived?: boolean
    usage?: number
}

export interface MultiSelectItem {
    label: string
    value: number | string
    archived?: boolean
}

export interface MultiSelectGroup {
    label: string
    items: MultiSelectItem[]
}

export interface SimpleSubject {
    id?: number,
    name: string,
    group: string
}