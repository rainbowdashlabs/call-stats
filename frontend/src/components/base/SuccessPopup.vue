<script setup lang="ts">
import {onMounted, onUnmounted, reactive} from 'vue'
import {bus, type SuccessEventPayload} from '../../events/bus'
import {t} from '../../i18n'

let idSeq = 1

const state = reactive({
  items: [] as { id: number, message: string }[]
})

function onSuccess(e: SuccessEventPayload) {
  const id = idSeq++
  state.items.push({ id, message: e.message })
  setTimeout(() => dismiss(id), 3000)
}

let off: (() => void) | null = null
onMounted(() => {
  off = bus.on<SuccessEventPayload>('success', onSuccess)
})

onUnmounted(() => { off?.(); off = null })

function dismiss(id: number) {
  const idx = state.items.findIndex(i => i.id === id)
  if (idx >= 0) state.items.splice(idx, 1)
}
</script>

<template>
  <div class="toast-container" v-if="state.items.length">
    <div v-for="it in state.items" :key="it.id" class="toast" style="border-left: 3px solid var(--c-band)">
      <font-awesome-icon class="icon" icon="fa-solid fa-circle-check" style="color: var(--c-band)"/>
      <div class="msg">{{ it.message }}</div>
      <button class="close" @click="dismiss(it.id)" :aria-label="t('common.close')">&times;</button>
    </div>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 18px;
  right: 18px;
  display: flex;
  flex-direction: column;
  gap: 9px;
  z-index: 1000;
}

.toast {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  max-width: 26rem;
  padding: 12px 34px 12px 13px;
  background: var(--c-surface);
  border: 1px solid var(--c-rule);
  border-radius: var(--radius-card);
  box-shadow: 0 8px 22px rgb(0 0 0 / 0.16);
}

.toast .icon {
  margin-top: 2px;
}

.msg {
  font-weight: 500;
  color: var(--c-ink);
}

.meta {
  margin-top: 3px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--c-muted);
}

.close {
  position: absolute;
  right: 8px;
  top: 8px;
  background: transparent;
  border: none;
  color: var(--c-faint);
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  padding: 2px;
}

.close:hover {
  color: var(--c-ink);
}
</style>
