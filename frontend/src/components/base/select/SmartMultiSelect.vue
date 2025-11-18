
<script setup lang="ts" generic="T">

import {type PropType, ref} from "vue";
import {select} from "../../../scripts/selection.ts";
import StandardButton from "../buttons/StandardButton.vue";

let props = defineProps({
  options: {
    type: Object as PropType<T[]>,
    required: true
  },
  value_mapper: {
    type: Function as PropType<(item: T) => string>,
    required: true
  },
  key_mapper: {
    type: Function as PropType<(item: T) => any>,
    required: true
  },
  show_empty: {
    type: Boolean,
    default: true
  }
})

const model = defineModel({type: Array as () => T[], default: []})


const currentMatches = ref<T[]>([])
if (props.show_empty) {
  currentMatches.value = props.options
}
const term = ref('')
const cursorItem = ref<T | null>(null)
const showDropdown = ref(false)

function keyDown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    if (cursorItem.value != null) {
      add(cursorItem.value)
      clear()
      update()
    }
    let matches = select<T>(props.options, props.value_mapper, term.value)
    if (matches.length === 1) {
      add(matches[0]!)
      clear()
      update()
    }
  }
  if (e.key === "ArrowDown") {
    if (cursorItem.value === null && currentMatches.value.length > 0) {
      cursorItem.value = currentMatches.value[0]! as T
    } else {
      let index = currentMatches.value.indexOf(cursorItem.value)
      if (index + 1 < currentMatches.value.length) {
        cursorItem.value = currentMatches.value[index + 1]! as T
      }
    }
  }

  if (e.key === "ArrowUp") {
    if (cursorItem.value !== null) {
      let index = currentMatches.value.indexOf(cursorItem.value)
      if (index > 0) {
        cursorItem.value = currentMatches.value[index - 1]! as T
      }
    }
  }
}

function clear() {
  term.value = ''
  cursorItem.value = null
}

function add(item: T) {
  if (model.value.indexOf(item) == -1) {
    model.value.push(item)
  }
}

function remove(item: T) {
  let index = model.value.indexOf(item)
  if (index != -1) {
    model.value.splice(index, 1)
  }
}

function update() {
  currentMatches.value = select<T>(props.options, props.value_mapper, term.value, props.show_empty)
  currentMatches.value = currentMatches.value.filter(v => model.value.indexOf(v as T) === -1)
  showDropdown.value = true
}

function onFocus() {
  showDropdown.value = true
  update()
}

function onBlur() {
  // Delay to allow click events to register
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

</script>

<template>
  <div>
    <div class="flex gap-2">
      <StandardButton class="bg-gray-200" v-for="item in model" :key="props.key_mapper(item)" @click="_ => remove(item)">
        {{ props.value_mapper(item) }}
      </StandardButton>
    </div>

    <div class="relative">
      <input type="text" v-model="term" @input="update" @keydown="keyDown" @focus="onFocus" @blur="onBlur" placeholder="search"
             class="bg-gray-800 text-gray-50 w-full"/>

      <div v-if="showDropdown && currentMatches.length > 0"
           class="absolute z-50 w-full mt-1 max-h-64 overflow-y-auto bg-gray-800 border border-gray-600 rounded shadow-lg">
        <div v-for="item in currentMatches" @click="() =>// @ts-ignore
         add(item)" :key="// @ts-ignore
         props.key_mapper(item)"
             class="cursor-pointer hover:bg-gray-700">
          <div v-if="cursorItem === item" class="bg-gray-600 text-gray-50 px-3 py-2">
            {{ // @ts-ignore
              props.value_mapper(item) }}
          </div>
          <div v-else class="bg-gray-800 text-gray-50 px-3 py-2">
            {{ // @ts-ignore
              props.value_mapper(item) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>