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
    type: Object as PropType<(item: T) => string>,
    required: true
  },
  key_mapper: {
    type: Object as PropType<(item: T) => any>,
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
}

</script>

<template>

  <div class="flex gap-1">
    <StandardButton class="bg-gray-200" v-for="item in model" :key="props.key_mapper(item)" @click="_ => remove(item)">
      {{ props.value_mapper(item) }}
    </StandardButton>
  </div>

  <input type="text" v-model="term" @input="update" @keydown="keyDown" placeholder="search"
         class="bg-gray-800 text-gray-50 w-full"/>

  <div v-for="item in currentMatches" @click="() => add(item)" :key="props.key_mapper(item)">
    <div v-if="cursorItem === item" class="bg-gray-600 text-gray-50">
      {{ props.value_mapper(item) }}
    </div>
    <div v-else class="bg-gray-800 text-gray-50">
      {{ props.value_mapper(item) }}
    </div>
  </div>

</template>

<style scoped>

</style>