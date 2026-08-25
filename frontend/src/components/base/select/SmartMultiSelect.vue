<script setup lang="ts">
import {ref, watch} from "vue"

const props = defineProps<{
  options: any[]
  valueMapper: (item: any) => string
  keyMapper: (item: any) => any
  showEmpty?: boolean
  placeholder?: string
}>()

const model = defineModel<any[]>({default: []})

const term = ref('')
const matches = ref<any[]>([])
const cursor = ref(-1)
const open = ref(false)

watch(() => props.options, () => { if (open.value) filter() })

function available(): any[] {
  return props.options.filter(o => !model.value.includes(o))
}

function filter() {
  const search = term.value.trim().toLowerCase()
  const pool = available()
  if (!search && props.showEmpty !== false) {
    matches.value = pool
  } else if (!search) {
    matches.value = []
  } else {
    matches.value = pool.filter(item =>
        props.valueMapper(item).toLowerCase().includes(search)
    )
  }
  cursor.value = -1
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

function onKeyDown(e: KeyboardEvent) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    cursor.value = Math.min(cursor.value + 1, matches.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    cursor.value = Math.max(cursor.value - 1, 0)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (cursor.value >= 0 && cursor.value < matches.value.length) {
      add(matches.value[cursor.value])
    } else if (matches.value.length === 1) {
      add(matches.value[0])
    }
  } else if (e.key === 'Escape') {
    open.value = false
    cursor.value = -1
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
</script>

<template>
  <div class="flex flex-col gap-2">
    <!-- Selected items as chips -->
    <div v-if="model.length > 0" class="flex gap-1 flex-wrap">
      <span v-for="item in model" :key="keyMapper(item)"
            class="inline-flex items-center gap-1 bg-gray-700 text-gray-100 px-2 py-1 rounded text-sm">
        {{ valueMapper(item) }}
        <button type="button" @click="remove(item)" class="text-gray-400 hover:text-white">&times;</button>
      </span>
    </div>

    <!-- Search input + dropdown -->
    <div class="relative">
      <input
          type="text"
          v-model="term"
          @input="filter"
          @keydown="onKeyDown"
          @focus="onFocus"
          @blur="onBlur"
          :placeholder="placeholder ?? 'Search...'"
          class="bg-gray-800 text-gray-50 w-full px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
      />
      <div v-if="open && matches.length > 0"
           class="absolute z-50 w-full mt-1 max-h-64 overflow-y-auto bg-gray-800 border border-gray-600 rounded shadow-lg">
        <div v-for="(item, i) in matches"
             :key="keyMapper(item)"
             @mousedown.prevent="add(item)"
             class="px-3 py-2 cursor-pointer"
             :class="i === cursor ? 'bg-gray-600' : 'hover:bg-gray-700'">
          {{ valueMapper(item) }}
        </div>
      </div>
    </div>
  </div>
</template>
