<script setup lang="ts">
import {nextTick, ref, watch} from 'vue'
import {t} from '../../../i18n'
import {rank} from '../../../scripts/selection'

const props = defineProps<{
  options: any[]
  valueMapper: (item: any) => string
  keyMapper: (item: any) => any
  weightMapper?: (item: any) => number
  hintMapper?: (item: any) => string
  showEmpty?: boolean
  emptyLimit?: number
  placeholder?: string
  strict?: boolean
  generator?: (value: string) => any
}>()

const model = defineModel<any>()
if (model.value === undefined && props.options.length > 0) {
  model.value = props.options[0]
}

const inputValue = ref(model.value ? props.valueMapper(model.value) : '')
const matches = ref<any[]>([])
const cursor = ref(0)
const open = ref(false)
const input = ref<HTMLInputElement | null>(null)
const list = ref<HTMLElement | null>(null)

watch(() => model.value, (val) => {
  inputValue.value = val ? props.valueMapper(val) : ''
})

watch(() => props.options, () => { if (open.value) filter() })

function pick(item: any) {
  model.value = item
  inputValue.value = props.valueMapper(item)
  open.value = false
  cursor.value = 0
}

function filter() {
  const term = inputValue.value.trim()
  if (!term && props.showEmpty === false) {
    matches.value = []
  } else {
    const ranked = rank(props.options, props.valueMapper, term, props.weightMapper)
    matches.value = !term && props.emptyLimit ? ranked.slice(0, props.emptyLimit) : ranked
  }
  if (!props.strict && props.generator) {
    model.value = props.generator(inputValue.value)
  }
  open.value = true
  cursor.value = 0
}

function highlighted(): any | null {
  return matches.value[cursor.value] ?? null
}

function moveCursor(delta: number) {
  const count = matches.value.length
  if (count === 0) return
  cursor.value = (cursor.value + delta + count) % count
  nextTick(scrollCursorIntoView)
}

function scrollCursorIntoView() {
  const option = list.value?.children[cursor.value] as HTMLElement | undefined
  option?.scrollIntoView({block: 'nearest'})
}

function accept(): boolean {
  const item = highlighted()
  if (item !== null) {
    pick(item)
    return true
  }
  if (!props.strict && props.generator) {
    pick(props.generator(inputValue.value))
    return true
  }
  return false
}

function onKeyDown(e: KeyboardEvent) {
  if (e.altKey && e.key >= '1' && e.key <= '9') {
    const item = matches.value[Number(e.key) - 1]
    if (item) {
      e.preventDefault()
      pick(item)
    }
    return
  }
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    moveCursor(1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    moveCursor(-1)
  } else if (e.key === 'Enter') {
    if (accept()) e.preventDefault()
  } else if (e.key === 'Tab') {
    accept()
  } else if (e.key === 'Escape') {
    open.value = false
  }
}

function onFocus() {
  filter()
}

function onBlur() {
  setTimeout(() => { open.value = false }, 150)
}

defineExpose({
  focus: () => input.value?.focus()
})
</script>

<template>
  <div class="relative w-full">
    <input
        ref="input"
        type="text"
        v-model="inputValue"
        @input="filter"
        @keydown="onKeyDown"
        @focus="onFocus"
        @blur="onBlur"
        :placeholder="placeholder ?? t('common.searchHint')"
        class="bg-gray-800 text-gray-50 w-full px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
    />
    <div v-if="open && matches.length > 0" ref="list"
         class="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-600 rounded shadow-lg max-h-60 overflow-y-auto">
      <div v-for="(item, i) in matches"
           :key="keyMapper(item)"
           @mousedown.prevent="pick(item)"
           class="flex items-baseline justify-between gap-3 px-3 py-2 cursor-pointer"
           :class="i === cursor ? 'bg-gray-600' : 'hover:bg-gray-700'">
        <span>{{ valueMapper(item) }}</span>
        <span v-if="hintMapper" class="text-xs text-gray-400 shrink-0">{{ hintMapper(item) }}</span>
      </div>
    </div>
  </div>
</template>
