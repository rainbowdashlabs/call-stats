<script setup lang="ts" generic="T">

import {type PropType, ref} from "vue";
import InfoButton from "../../buttons/derivates/InfoButton.vue";

let props = defineProps({
  key: {
    type: Object as PropType<T>,
    optional: false
  },
  value: {
    type: String,
    optional: false
  }
})

let selected = ref(false)

const emit = defineEmits({
  select: null,
  deselect: null
})

function click() {
  if (selected.value) {
    emit("deselect", props.key)
  } else {
    emit("select", props.key)
  }
  selected.value = !selected.value
}

</script>

<template>
  <Button :class="selected ? 'bg-green-500' : 'bg-blue-400'" @click="click">{{ value }}</Button>
</template>

<style scoped>

</style>