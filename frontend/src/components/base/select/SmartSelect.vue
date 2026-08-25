<script setup lang="ts">
import {ref, watch} from 'vue'

const props = defineProps<{
  options: any[]
  valueMapper: (item: any) => string
  keyMapper: (item: any) => any
  showEmpty?: boolean
  placeholder?: string
  strict?: boolean
  generator?: (value: string) => any
}>()

const model = defineModel<any>()
if (model.value === undefined && props.options.length > 0) {
  model.value = props.options[0]
}

const inputValue = ref(model.value ? props.valueMapper(model.value) : '')
const matches = ref<any[]>(props.showEmpty !== false ? [...props.options] : [])
const cursor = ref(-1)
const open = ref(false)

watch(() => model.value, (val) => {
  if (val) inputValue.value = props.valueMapper(val)
})

watch(() => props.options, (opts) => {
  if (props.showEmpty !== false) matches.value = [...opts]
})

function pick(item: any) {
  model.value = item
  inputValue.value = props.valueMapper(item)
  open.value = false
  cursor.value = -1
}

function filter() {
  const term = inputValue.value.trim().toLowerCase()
  if (!term && props.showEmpty !== false) {
    matches.value = [...props.options]
  } else if (!term) {
    matches.value = []
  } else {
    matches.value = props.options.filter(item =>
        props.valueMapper(item).toLowerCase().includes(term)
    )
  }
  if (!props.strict && props.generator) {
    model.value = props.generator(inputValue.value)
  }
  open.value = true
  cursor.value = -1
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
      pick(matches.value[cursor.value])
    } else if (matches.value.length === 1 && props.strict) {
      pick(matches.value[0])
    } else if (!props.strict && props.generator) {
      pick(props.generator(inputValue.value))
    }
  } else if (e.key === 'Escape') {
    open.value = false
    cursor.value = -1
  }
}

function onFocus() {
  filter()
}

function onBlur() {
  setTimeout(() => { open.value = false }, 150)
}
</script>

<template>
  <div class="relative w-full">
    <input
        type="text"
        v-model="inputValue"
        @input="filter"
        @keydown="onKeyDown"
        @focus="onFocus"
        @blur="onBlur"
        :placeholder="placeholder ?? 'Type to search...'"
        class="bg-gray-800 text-gray-50 w-full px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
    />
    <div v-if="open && matches.length > 0"
         class="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-600 rounded shadow-lg max-h-60 overflow-y-auto">
      <div v-for="(item, i) in matches"
           :key="keyMapper(item)"
           @mousedown.prevent="pick(item)"
           class="px-3 py-2 cursor-pointer"
           :class="i === cursor ? 'bg-gray-600' : 'hover:bg-gray-700'">
        {{ valueMapper(item) }}
      </div>
    </div>
  </div>
</template>
