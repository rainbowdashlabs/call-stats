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
  }
})

const model = defineModel({type: Number, required: true})

watch(model, (value) => {
  console.log(`Model value updated to ${value}`)
  currentValue.value = value
  clampAndPropagateToModel(value)
})

const currentValue = ref<number>(model.value)

function clampAndPropagateToModel(value?: number){
  if (!value) return
  if (value > props.max) {
    currentValue.value = props.max
  }
  if (value < props.min) {
    currentValue.value = props.min
  }
  model.value = currentValue.value!
}

clampAndPropagateToModel(model.value)

watch(currentValue, clampAndPropagateToModel)

const emit = defineEmits(["overflowUp", "overflowDown"])

function handleDown() {
  console.log(currentValue.value)
  console.log("down")
  if (currentValue.value - 1 < props.min) {
    currentValue.value = props.max
    emit("overflowDown")
  } else {
    currentValue.value -= 1
  }
  console.log(currentValue.value)
}

function handleUp() {
  console.log(currentValue.value)
  console.log("up")
  if (currentValue.value + 1 > props.max) {
    currentValue.value = props.min
    emit("overflowUp")
  } else {
    currentValue.value += 1
  }
  console.log(currentValue.value)
}

</script>

<template>
  <div class="gap-2">
    <simple-button class="bg-secondary rounded-t-md" @click="handleUp">
      <font-awesome-icon icon="fa-solid fa-angle-up"/>
    </simple-button>
    <input type="text" pattern="[0-9]*" :min="props.min" :max="props.max" v-model="currentValue" @keydown.down.prevent="handleDown"
           @keydown.up.prevent="handleUp" :style="{width: props.max.toString().length + 2 + 'ch'}">
    <simple-button class="bg-secondary rounded-b-md" @click="handleDown">
      <font-awesome-icon icon="fa-solid fa-angle-down"/>
    </simple-button>
  </div>
</template>

<style scoped>
input{
  text-align: center;
}
</style>