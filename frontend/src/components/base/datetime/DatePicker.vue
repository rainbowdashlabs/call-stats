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

const dayPicker = ref<InstanceType<typeof NumberPicker> | null>(null)
const monthPicker = ref<InstanceType<typeof NumberPicker> | null>(null)
const yearPicker = ref<InstanceType<typeof NumberPicker> | null>(null)

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

watch(model, (value) => {
  updating = true
  day.value = value.day
  month.value = value.month
  year.value = value.year
  recalcMaxDays()
  updating = false
})

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

defineExpose({
  focus: () => dayPicker.value?.focus()
})
</script>

<template>
  <div class="picker-group">
    <NumberPicker ref="dayPicker" :max="maxDays" :min="1" v-model="day" @overflowUp="dayOverflowUp"
                  @overflowDown="dayOverflowDown" @advance="monthPicker?.focus()"/>
    <span class="sep">.</span>
    <NumberPicker ref="monthPicker" :max="12" :min="1" v-model="month" @overflowUp="monthOverflowUp"
                  @overflowDown="monthOverflowDown" @advance="yearPicker?.focus()"/>
    <span class="sep">.</span>
    <NumberPicker ref="yearPicker" :max="2100" :min="1900" v-model="year"/>
  </div>
</template>

<style scoped>
.picker-group {
  display: flex;
  align-items: flex-end;
  gap: 4px;
}

.picker-group .sep {
  color: var(--c-faint);
  padding-bottom: 8px;
}
</style>
