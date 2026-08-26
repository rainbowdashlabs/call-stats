<script setup lang="ts">

import {ref, watch} from "vue";
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
  <div class="picker">
    <span v-if="props.label" class="picker-label">{{ props.label }}</span>
    <div class="picker-body">
      <input ref="input" type="text" inputmode="numeric" pattern="[0-9]*" :aria-label="props.label"
             @focusin="($event.target as HTMLInputElement).select()"
             :min="props.min" :max="props.max" v-model="currentValue" @input="handleInput"
             @keydown.down.prevent="handleDown" @keydown.up.prevent="handleUp"
             :style="{width: `calc(${digits}ch + 18px)`}">
      <div class="picker-steps">
        <button type="button" tabindex="-1" @click="handleUp" :aria-label="props.label">
          <font-awesome-icon icon="fa-solid fa-angle-up"/>
        </button>
        <button type="button" tabindex="-1" @click="handleDown" :aria-label="props.label">
          <font-awesome-icon icon="fa-solid fa-angle-down"/>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.picker {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.picker-label {
  font-family: var(--font-condensed);
  font-weight: 600;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--c-muted);
}

.picker-body {
  display: flex;
  align-items: stretch;
  height: 38px;
  border: 1px solid var(--c-rule);
  border-radius: var(--radius-control);
  background: var(--c-surface);
  overflow: hidden;
}

.picker-body:focus-within {
  border-color: var(--c-focus);
  box-shadow: 0 0 0 1px var(--c-focus);
}

input {
  border: none;
  outline: none;
  background: transparent;
  color: var(--c-ink);
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  font-size: 15px;
  text-align: center;
  padding: 0 6px;
  min-width: 0;
}

.picker-steps {
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--c-hairline);
}

.picker-steps button {
  flex: 1;
  width: 22px;
  border: none;
  padding: 0;
  background: transparent;
  color: var(--c-faint);
  font-size: 10px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.picker-steps button:hover {
  background: var(--c-raised);
  color: var(--c-ink);
}

.picker-steps button:first-child {
  border-bottom: 1px solid var(--c-hairline);
}
</style>
