<script setup lang="ts">

import {type PropType, ref, watch} from "vue";
import NumberPicker from "./NumberPicker.vue";
import type {ADateTime} from "../../../scripts/datetime.ts";

const props = defineProps({
  seconds: {
    type: Boolean,
    required: false,
    default: false
  }
})

const model = defineModel({type: Object as PropType<ADateTime>, required: true})

if (!props.seconds) {
  model.value.second = 0
}

const hour = ref<number>(model.value.hour)
const minute = ref<number>(model.value.minute)
const seconds = ref<number>(model.value.second)

watch(hour, (value) => model.value.hour = value)
watch(minute, (value) => model.value.minute = value)
watch(seconds, (value) => model.value.second = value)

</script>

<template>
  <div class="flex bg-bgmd items-center p-2 rounded-md">
    <NumberPicker :max="24" :min="0" v-model="hour" label="Stunde"/>
    :
    <NumberPicker :max="59" :min="0" v-model="minute" label="Minute"/>
    <div v-if="props.seconds"> : </div>
    <NumberPicker v-if="props.seconds" max="0" min="59" v-model="seconds" label="Sekunde"/>
  </div>

</template>

<style scoped>

</style>