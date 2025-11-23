<script setup lang="ts">

import {type PropType, watch} from "vue";
import DatePicker from "./DatePicker.vue";
import TimePicker from "./TimePicker.vue";
import type {ADateTime} from "../../../scripts/datetime.ts";

const model = defineModel({type: Object as PropType<ADateTime>, required: true})

const props = defineProps({
  seconds: {
    type: Boolean,
    required: false,
    default: false
  }
})

watch(model, (value) => {
  console.log(`Updated datetime to ${value}`)
}, {deep: true})

</script>

<template>
  <div class="flex gap-2 bg-bgmd rounded-md">
    <DatePicker v-model="model"/>
    <TimePicker v-model="model" :seconds="props.seconds"/>
  </div>
</template>

<style scoped>

</style>