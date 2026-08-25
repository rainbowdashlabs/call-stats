<script setup lang="ts">

import {type PropType, ref, watch} from "vue";
import NumberPicker from "./NumberPicker.vue";
import {ADateTime, getCurrentDay, getCurrentMonth, getCurrentYear, getDaysInMonth} from "../../../scripts/datetime.ts";

const model = defineModel({
  type: Object as PropType<ADateTime>,
  required: true
})

const day = ref<number>(model.value.day ?? getCurrentDay())
const month = ref<number>(model.value.month ?? getCurrentMonth())
const year = ref<number>(model.value.year ?? getCurrentYear())
const maxDays = ref<number>(getDaysInMonth(year.value, month.value))

let updating = false

function sync() {
  if (updating) return
  updating = true
  model.value.day = day.value
  model.value.month = month.value
  model.value.year = year.value
  updating = false
}

function recalcMaxDays() {
  maxDays.value = getDaysInMonth(year.value, month.value)
  if (day.value > maxDays.value) {
    day.value = maxDays.value
  }
}

watch(day, sync)
watch(month, () => { recalcMaxDays(); sync() })
watch(year, () => { recalcMaxDays(); sync() })

function dayOverflowUp() {
  if (month.value >= 12) {
    month.value = 1
    year.value += 1
  } else {
    month.value += 1
  }
}

function dayOverflowDown() {
  if (month.value <= 1) {
    month.value = 12
    year.value -= 1
  } else {
    month.value -= 1
  }
}

function monthOverflowUp() {
  year.value += 1
}

function monthOverflowDown() {
  year.value -= 1
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
