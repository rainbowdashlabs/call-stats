export interface Subject {
    id?: number
    group: string
    name: string
}

export interface MultiSelectItem {
    label: string
    value: number | string
}

export interface MultiSelectGroup {
    label: string
    items: MultiSelectItem[]
}
