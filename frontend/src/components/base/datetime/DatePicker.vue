<script setup lang="ts">

import {type PropType, ref, watch} from "vue";
import NumberPicker from "./NumberPicker.vue";
import {ADateTime, getCurrentDay, getCurrentMonth, getCurrentYear, getDaysInMonth} from "../../../scripts/datetime.ts";

const day = ref<number>(getCurrentDay())
const month = ref<number>(getCurrentMonth())
const year = ref<number>(getCurrentYear())
const maxDays = ref<number>(getDaysInMonth(year.value, month.value))

const model = defineModel({
  type: Object as PropType<ADateTime>,
  required: true
})

watch(maxDays, (value) => {
  console.log("enforce max days")
  day.value = Math.min(value, day.value)
})

watch(day, () => {
  model.value.day = day.value
})

watch(month, (value) => {
  if (value > 12) {
    console.log("Year up")
    month.value = 1
    year.value += 1
  }
  if (value == 0) {
    console.log("Year down")
    month.value = 12
    year.value -= 1
  }
  maxDays.value = getDaysInMonth(year.value, value)
  model.value.month = month.value
})

watch(year, (value) => {
  maxDays.value = getDaysInMonth(value, month.value)
  model.value.year = year.value
})

function dayOverflowUp() {
  month.value += 1
}

function dayOverflowDown() {
  month.value -= 1
}

function monthOverflowDown() {
  year.value -= 1
}

function monthOverflowUp() {
  year.value += 1
}
</script>

<template>
  <div class="flex bg-bgmd items-center p-2 rounded-md">
    <NumberPicker :max="maxDays" :min="1" v-model="day" @overflowUp="dayOverflowUp" @overflowDown="dayOverflowDown"/>
.
    <NumberPicker :max="12" :min="1" v-model="month" @overflowUp="monthOverflowUp" @overflowDown="monthOverflowDown"/>
.
    <NumberPicker :max="2100" :min="1900" v-model="year"/>
  </div>
</template>

<style scoped>

</style>