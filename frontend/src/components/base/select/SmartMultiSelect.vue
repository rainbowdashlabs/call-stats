<script setup lang="ts">
import {nextTick, ref, watch} from "vue"
import {t} from "../../../i18n"
import {rank} from "../../../scripts/selection"

const props = defineProps<{
  options: any[]
  valueMapper: (item: any) => string
  keyMapper: (item: any) => any
  weightMapper?: (item: any) => number
  hintMapper?: (item: any) => string
  showEmpty?: boolean
  emptyLimit?: number
  placeholder?: string
}>()

const model = defineModel<any[]>({default: []})

const term = ref('')
const matches = ref<any[]>([])
const cursor = ref(0)
const open = ref(false)
const input = ref<HTMLInputElement | null>(null)
const list = ref<HTMLElement | null>(null)

watch(() => props.options, () => { if (open.value) filter() })

function available(): any[] {
  return props.options.filter(o => !model.value.includes(o))
}

function filter() {
  const search = term.value.trim()
  if (!search && props.showEmpty === false) {
    matches.value = []
  } else {
    const ranked = rank(available(), props.valueMapper, search, props.weightMapper)
    matches.value = !search && props.emptyLimit ? ranked.slice(0, props.emptyLimit) : ranked
  }
  cursor.value = 0
}

function onInput() {
  open.value = true
  filter()
}

function add(item: any) {
  if (!model.value.includes(item)) {
    model.value = [...model.value, item]
  }
  term.value = ''
  filter()
}

function remove(item: any) {
  model.value = model.value.filter(v => v !== item)
  filter()
}

function highlighted(): any | null {
  return matches.value[cursor.value] ?? null
}

function moveCursor(delta: number) {
  const count = matches.value.length
  if (count === 0) return
  cursor.value = (cursor.value + delta + count) % count
  nextTick(scrollCursorIntoView)
}

function scrollCursorIntoView() {
  const option = list.value?.children[cursor.value] as HTMLElement | undefined
  option?.scrollIntoView({block: 'nearest'})
}

function onKeyDown(e: KeyboardEvent) {
  if (e.altKey && e.key >= '1' && e.key <= '9') {
    const item = matches.value[Number(e.key) - 1]
    if (item) {
      e.preventDefault()
      add(item)
    }
    return
  }
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    moveCursor(1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    moveCursor(-1)
  } else if (e.key === 'Enter' || e.key === ',' || e.key === ';') {
    const item = highlighted()
    if (item) {
      e.preventDefault()
      add(item)
    }
  } else if (e.key === 'Tab') {
    const item = highlighted()
    if (item && term.value.trim()) add(item)
  } else if (e.key === 'Escape') {
    open.value = false
  } else if (e.key === 'Backspace' && !term.value && model.value.length > 0) {
    remove(model.value[model.value.length - 1])
  }
}

function onFocus() {
  open.value = true
  filter()
}

function onBlur() {
  setTimeout(() => { open.value = false }, 150)
}

defineExpose({
  focus: () => input.value?.focus()
})
</script>

<template>
  <div class="flex flex-col gap-2">
    <div v-if="model.length > 0" class="flex gap-1 flex-wrap">
      <span v-for="item in model" :key="keyMapper(item)"
            class="chip">
        {{ valueMapper(item) }}
        <button type="button" tabindex="-1" @click="remove(item)" >&times;</button>
      </span>
    </div>

    <div class="relative">
      <input
          ref="input"
          type="text"
          v-model="term"
          @input="onInput"
          @keydown="onKeyDown"
          @focus="onFocus"
          @blur="onBlur"
          :placeholder="placeholder ?? t('common.search')"
          class="field"
      />
      <div v-if="open && matches.length > 0" ref="list"
           class="menu">
        <div v-for="(item, i) in matches"
             :key="keyMapper(item)"
             @mousedown.prevent="add(item)"
             class="option"
             :class="{active: i === cursor}">
          <span>{{ valueMapper(item) }}</span>
          <span v-if="hintMapper" class="option-hint">{{ hintMapper(item) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  height: 27px;
  padding: 0 9px;
  background: var(--c-raised);
  border: 1px solid var(--c-rule);
  border-radius: 3px;
  font-size: 14px;
  color: var(--c-ink);
}

.chip button {
  border: none;
  background: transparent;
  color: var(--c-faint);
  cursor: pointer;
  padding: 0;
  font-size: 13px;
  line-height: 1;
}

.chip button:hover {
  color: var(--c-signal);
}

.menu {
  position: absolute;
  z-index: 50;
  width: 100%;
  margin-top: -1px;
  max-height: 260px;
  overflow-y: auto;
  background: var(--c-surface);
  border: 1px solid var(--c-rule);
  border-radius: 0 0 var(--radius-control) var(--radius-control);
  box-shadow: 0 6px 16px rgb(0 0 0 / 0.12);
}

.option {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding: 9px 11px;
  cursor: pointer;
  border-top: 1px solid var(--c-hairline);
}

.option:first-child {
  border-top: none;
}

.option:hover {
  background: var(--c-hairline);
}

.option.active {
  background: var(--c-raised);
  box-shadow: inset 2px 0 0 var(--c-signal);
}

.option-hint {
  font-family: var(--font-condensed);
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--c-muted);
  flex-shrink: 0;
}
</style>
