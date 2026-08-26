<script setup lang="ts">

import {type PropType, ref} from "vue";
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

const datePicker = ref<InstanceType<typeof DatePicker> | null>(null)

defineExpose({
  focus: () => datePicker.value?.focus()
})
</script>

<template>
  <div class="flex flex-wrap gap-x-3 gap-y-2 items-end">
    <DatePicker ref="datePicker" v-model="model"/>
    <TimePicker v-model="model" :seconds="props.seconds"/>
  </div>
</template>

<style scoped>

</style>