<script setup lang="ts">

import {type PropType, ref, watch} from "vue";
import NumberPicker from "./NumberPicker.vue";
import type {ADateTime} from "../../../scripts/datetime.ts";
import {t} from "../../../i18n";

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

const hourPicker = ref<InstanceType<typeof NumberPicker> | null>(null)
const minutePicker = ref<InstanceType<typeof NumberPicker> | null>(null)
const secondPicker = ref<InstanceType<typeof NumberPicker> | null>(null)

watch(hour, (value) => model.value.hour = value)
watch(minute, (value) => model.value.minute = value)
watch(seconds, (value) => model.value.second = value)

watch(model, (value) => {
  hour.value = value.hour
  minute.value = value.minute
  seconds.value = value.second
})

defineExpose({
  focus: () => hourPicker.value?.focus()
})
</script>

<template>
  <div class="flex bg-bgmd items-center p-2 rounded-md">
    <NumberPicker ref="hourPicker" :max="23" :min="0" v-model="hour" :label="t('common.hour')"
                  @advance="minutePicker?.focus()"/>
    :
    <NumberPicker ref="minutePicker" :max="59" :min="0" v-model="minute" :label="t('common.minute')"
                  @advance="props.seconds ? secondPicker?.focus() : undefined"/>
    <div v-if="props.seconds"> : </div>
    <NumberPicker v-if="props.seconds" ref="secondPicker" :max="59" :min="0" v-model="seconds"
                  :label="t('common.second')"/>
  </div>

</template>

<style scoped>

</style>
