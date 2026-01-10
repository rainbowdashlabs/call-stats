
<script setup lang="ts" generic="T">

import {type PropType, ref} from "vue";
import {select} from "../../../scripts/selection.ts";
import StandardButton from "../buttons/StandardButton.vue";
import ButtonMultiSelectButton from "./buttonmultistelect/ButtonMultiSelectButton.vue";

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

</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <ButtonMultiSelectButton v-for="item in options" :key="key_mapper(item)" :value="value_mapper(item)" @select="add(item)" @deselect="remove(item)"/>
  </div>
</template>

<style scoped>

</style>