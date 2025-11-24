<script setup lang="ts" generic="T">
import {ref, type PropType} from 'vue'
import {select} from "../../../scripts/selection.ts";

const props = defineProps({
  options: {
    type: Object as PropType<T[]>,
    required: true
  },
  value_mapper: {
    type: Function as PropType<(item: T | string) => string>,
    required: true
  },
  key_mapper: {
    type: Function as PropType<(item: T) => any>,
    required: true
  },
  show_empty: {
    type: Boolean,
    default: true
  },
  placeholder: {
    type: String,
    default: 'Type to search...'
  },
  strict: {
    type: Boolean,
    default: false
  },
  generator: {
    type: Function as PropType<(value: string) => T>,
    required: false,
    default: (v: string) => v
  }
})

const model = defineModel({type: Object as () => T | string, default: null})
model.value = props.options[0]!
const input_value = ref<string>('')
const currentMatches = ref<T[]>([])
if (props.show_empty) {
  currentMatches.value = props.options
}
const cursorItem = ref<T | null>(null)
const showDropdown = ref(false)

function set(value: T) {
  console.log(value)
  input_value.value = props.value_mapper(value)
  model.value = value
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    if (cursorItem.value != null) {
      set(cursorItem.value)
      showDropdown.value = false
    } else {
      let matches = select<T>(props.options, props.value_mapper, props.value_mapper(model.value))
      if (matches.length === 1 && props.strict) {
        set(matches[0]!)
        showDropdown.value = false
      } else if (!props.strict) {
        console.log("Unknown value. Using current value as new model value")
        set(props.generator(input_value.value))
      }
    }
    return
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (cursorItem.value === null && currentMatches.value.length > 0) {
      cursorItem.value = currentMatches.value[0]! as T
    } else {
      let index = currentMatches.value.indexOf(cursorItem.value)
      if (index + 1 < currentMatches.value.length) {
        cursorItem.value = currentMatches.value[index + 1]! as T
      }
    }
  }

  if (e.key === 'ArrowUp') {
    if (cursorItem.value !== null) {
      let index = currentMatches.value.indexOf(cursorItem.value)
      if (index > 0) {
        cursorItem.value = currentMatches.value[index - 1]! as T
      }
    }
  }

  if (e.key === 'Escape') {
    showDropdown.value = false
    cursorItem.value = null
  }
}

function onFocus() {
  showDropdown.value = true
  update()
}

function update() {
  if (model.value != null) {
    currentMatches.value = select<T>(props.options, props.value_mapper, input_value.value, props.show_empty)
  }
  if (!props.strict) {
    set(props.generator(input_value.value))
  }
  showDropdown.value = true
}

function onBlur() {
  // Delay to allow click events to register
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

</script>

<template>
  <div @keydown="handleKeyDown" class="relative w-full">
    <input
        type="text"
        v-model="input_value"
        @input="update"
        @focus="onFocus"
        @blur="onBlur"
        :placeholder="props.placeholder"
        class="bg-gray-800 text-gray-50 w-full px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
    />

    <div
        v-if="showDropdown && currentMatches.length > 0"
        class="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-600 rounded shadow-lg max-h-60 overflow-y-auto"
    >
      <!-- @ts-ignore-->
      <div v-for="item in currentMatches" @click="() => // @ts-ignore
       set(item)" :key="// @ts-ignore
       props.key_mapper(item)"
           class="cursor-pointer hover:bg-gray-700">
        <div v-if="cursorItem === item" class="bg-gray-600 text-gray-50 px-3 py-2">

          {{
            // @ts-ignore
            props.value_mapper(item)
          }}
        </div>
        <div v-else class="bg-gray-800 text-gray-50 px-3 py-2">
          {{
            // @ts-ignore
            props.value_mapper(item)
          }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>