<script setup lang="ts">
import {nextTick, ref, watch} from "vue"
import {t} from "../../../i18n"
import {rank} from "../../../scripts/selection"

const props = defineProps<{
  options: any[]
  valueMapper: (item: any) => string
  keyMapper: (item: any) => any
  weightMapper?: (item: any) => number
  hintMapper?: (item: any) => string
  showEmpty?: boolean
  emptyLimit?: number
  placeholder?: string
}>()

const model = defineModel<any[]>({default: []})

const term = ref('')
const matches = ref<any[]>([])
const cursor = ref(0)
const open = ref(false)
const input = ref<HTMLInputElement | null>(null)
const list = ref<HTMLElement | null>(null)

watch(() => props.options, () => { if (open.value) filter() })

function available(): any[] {
  return props.options.filter(o => !model.value.includes(o))
}

function filter() {
  const search = term.value.trim()
  if (!search && props.showEmpty === false) {
    matches.value = []
  } else {
    const ranked = rank(available(), props.valueMapper, search, props.weightMapper)
    matches.value = !search && props.emptyLimit ? ranked.slice(0, props.emptyLimit) : ranked
  }
  cursor.value = 0
}

function add(item: any) {
  if (!model.value.includes(item)) {
    model.value = [...model.value, item]
  }
  term.value = ''
  filter()
}

function remove(item: any) {
  model.value = model.value.filter(v => v !== item)
  filter()
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

function onKeyDown(e: KeyboardEvent) {
  if (e.altKey && e.key >= '1' && e.key <= '9') {
    const item = matches.value[Number(e.key) - 1]
    if (item) {
      e.preventDefault()
      add(item)
    }
    return
  }
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    moveCursor(1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    moveCursor(-1)
  } else if (e.key === 'Enter' || e.key === ',' || e.key === ';') {
    const item = highlighted()
    if (item) {
      e.preventDefault()
      add(item)
    }
  } else if (e.key === 'Tab') {
    const item = highlighted()
    if (item && term.value.trim()) add(item)
  } else if (e.key === 'Escape') {
    open.value = false
  } else if (e.key === 'Backspace' && !term.value && model.value.length > 0) {
    remove(model.value[model.value.length - 1])
  }
}

function onFocus() {
  open.value = true
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
  <div class="flex flex-col gap-2">
    <div v-if="model.length > 0" class="flex gap-1 flex-wrap">
      <span v-for="item in model" :key="keyMapper(item)"
            class="inline-flex items-center gap-1 bg-gray-700 text-gray-100 px-2 py-1 rounded text-sm">
        {{ valueMapper(item) }}
        <button type="button" tabindex="-1" @click="remove(item)" class="text-gray-400 hover:text-white">&times;</button>
      </span>
    </div>

    <div class="relative">
      <input
          ref="input"
          type="text"
          v-model="term"
          @input="filter"
          @keydown="onKeyDown"
          @focus="onFocus"
          @blur="onBlur"
          :placeholder="placeholder ?? t('common.search')"
          class="bg-gray-800 text-gray-50 w-full px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
      />
      <div v-if="open && matches.length > 0" ref="list"
           class="absolute z-50 w-full mt-1 max-h-64 overflow-y-auto bg-gray-800 border border-gray-600 rounded shadow-lg">
        <div v-for="(item, i) in matches"
             :key="keyMapper(item)"
             @mousedown.prevent="add(item)"
             class="flex items-baseline justify-between gap-3 px-3 py-2 cursor-pointer"
             :class="i === cursor ? 'bg-gray-600' : 'hover:bg-gray-700'">
          <span>{{ valueMapper(item) }}</span>
          <span v-if="hintMapper" class="text-xs text-gray-400 shrink-0">{{ hintMapper(item) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
