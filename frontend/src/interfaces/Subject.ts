export interface Subject {
    id?: number
    group: string
    name: string
}

export interface MultiSelectItem {
    label: string
    value: number
}

export interface MultiSelectGroup {
    label: string
    items: MultiSelectItem[]
}
