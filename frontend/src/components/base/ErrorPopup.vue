<script setup lang="ts">
import {onMounted, onUnmounted, reactive} from 'vue'
import {bus, type ErrorEventPayload} from '../../events/bus'

let idSeq = 1

const state = reactive({
  items: [] as { id: number, message: string, code?: string | number }[]
})

function onError(e: ErrorEventPayload) {
  state.items.push({ id: idSeq++, message: e.message, code: e.code })
}

let off: (() => void) | null = null
onMounted(() => {
  off = bus.on<ErrorEventPayload>('error', onError)
})

onUnmounted(() => { off?.(); off = null })

function dismiss(id: number) {
  const idx = state.items.findIndex(i => i.id === id)
  if (idx >= 0) state.items.splice(idx, 1)
}
</script>

<template>
  <div class="error-container" v-if="state.items.length">
    <div v-for="it in state.items" :key="it.id" class="error-card">
      <div class="msg">{{ it.message }}</div>
      <div class="meta" v-if="it.code">Code: {{ it.code }}</div>
      <button class="close" @click="dismiss(it.id)" aria-label="Close">×</button>
    </div>
  </div>
</template>

<style scoped>
.error-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 1000;
}
.error-card {
  position: relative;
  max-width: 28rem;
  background: #7f1d1d; /* dark red */
  color: #fff;
  border: 1px solid rgba(255,255,255,0.2);
  border-left: 4px solid #ef4444; /* accent */
  padding: 0.75rem 2rem 0.75rem 0.75rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.msg { font-weight: 600; }
.meta { opacity: 0.85; font-size: 0.85rem; margin-top: 0.25rem; }
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
