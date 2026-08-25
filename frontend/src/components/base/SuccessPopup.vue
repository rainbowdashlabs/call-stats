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
  <div class="success-container" v-if="state.items.length">
    <div v-for="it in state.items" :key="it.id" class="success-card">
      <div class="msg">{{ it.message }}</div>
      <button class="close" @click="dismiss(it.id)" :aria-label="t('common.close')">&times;</button>
    </div>
  </div>
</template>

<style scoped>
.success-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 1000;
}
.success-card {
  position: relative;
  max-width: 28rem;
  background: #14532d;
  color: #fff;
  border: 1px solid rgba(255,255,255,0.2);
  border-left: 4px solid #22c55e;
  padding: 0.75rem 2rem 0.75rem 0.75rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.msg { font-weight: 600; }
.close {
  position: absolute;
  right: 0.25rem;
  top: 0.25rem;
  background: transparent;
  color: #fff;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
}
.close:focus-visible { outline: 2px solid #fff; border-radius: 0.25rem; }
</style>
