<script setup lang="ts">

import {ref, watch} from "vue";
import SimpleButton from "../buttons/SimpleButton.vue";
import {FontAwesomeIcon} from "@fortawesome/vue-fontawesome";

const props = defineProps({
  min: {
    type: Number,
    required: true
  },
  max: {
    type: Number,
    required: true
  },
  label: {
    type: String,
    required: false
  }
})

const model = defineModel({type: Number, required: true})
const currentValue = ref<number>(Math.min(props.max, Math.max(props.min, model.value)))
const input = ref<HTMLInputElement | null>(null)

watch(model, (value) => {
  const clamped = Math.min(props.max, Math.max(props.min, value))
  if (currentValue.value !== clamped) {
    currentValue.value = clamped
  }
})

watch(currentValue, (value) => {
  const num = Number(value)
  if (isNaN(num)) return
  const clamped = Math.min(props.max, Math.max(props.min, num))
  if (clamped !== currentValue.value) {
    currentValue.value = clamped
  }
  if (model.value !== clamped) {
    model.value = clamped
  }
})

watch(() => props.max, () => {
  const clamped = Math.min(props.max, Math.max(props.min, currentValue.value))
  if (currentValue.value !== clamped) {
    currentValue.value = clamped
  }
})

const emit = defineEmits(["overflowUp", "overflowDown", "advance"])

const digits = props.max.toString().length

function handleUp() {
  if (currentValue.value + 1 > props.max) {
    currentValue.value = props.min
    emit("overflowUp")
  } else {
    currentValue.value += 1
  }
}

function handleDown() {
  if (currentValue.value - 1 < props.min) {
    currentValue.value = props.max
    emit("overflowDown")
  } else {
    currentValue.value -= 1
  }
}

function handleInput(event: Event) {
  const typed = (event.target as HTMLInputElement).value.replace(/\D/g, '')
  if (typed.length >= digits) {
    emit("advance")
  }
}

defineExpose({
  focus: () => {
    input.value?.focus()
    input.value?.select()
  }
})
</script>

<template>
  <div class="gap-2">
    <SimpleButton class="bg-secondary rounded-t-md" @click="handleUp">
      <font-awesome-icon icon="fa-solid fa-angle-up"/>
    </SimpleButton>
    <input ref="input" type="text" pattern="[0-9]*" @focusin="($event.target as HTMLInputElement).select()"
           :min="props.min" :max="props.max" v-model="currentValue" @input="handleInput"
           @keydown.down.prevent="handleDown" @keydown.up.prevent="handleUp"
           :style="{width: props.max.toString().length + 2 + 'ch'}">
    <SimpleButton class="bg-secondary rounded-b-md" @click="handleDown">
      <font-awesome-icon icon="fa-solid fa-angle-down"/>
    </SimpleButton>
  </div>
</template>

<style scoped>
input{
  text-align: center;
}
</style>
