export interface Subject extends SimpleSubject {
}

export interface MultiSelectItem {
    label: string
    value: number | string
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