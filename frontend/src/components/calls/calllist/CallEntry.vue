<script setup lang="ts">
import {computed, type PropType} from "vue";
import type {FullCall} from "../../../interfaces/Call.ts";
import {dayPosition, formatDate, formatDuration} from "../../../scripts/datetime.ts";
import router from "../../../router";
import {t} from "../../../i18n";

const props = defineProps({
  call: {
    type: Object as PropType<FullCall>,
    required: true
  }
})

const band = computed(() => dayPosition(props.call.start, props.call.end))

const started = computed(() => {
  const date = new Date(props.call.start as string)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
})

const minutes = computed(() =>
    (new Date(props.call.end as string).getTime() - new Date(props.call.start as string).getTime()) / 60000)

async function load() {
  await router.push({name: "Call", params: {"id": props.call!.id}})
}
</script>

<template>
  <div class="call-row" :class="{aborted: !!call.abort_reason}" @click="load" role="button" tabindex="0"
       @keydown.enter="load">
    <div class="min-w-0">
      <div class="truncate font-medium">{{ call.subjects.map(s => s.name).join(' + ') }}</div>
      <div class="flex items-center gap-2 mt-0.5">
        <span class="tabular text-xs text-muted">{{ formatDate(call.start as string) }}</span>
        <span v-if="call.abort_reason" class="label" style="color: var(--c-signal-ink)">{{ call.abort_reason }}</span>
        <span v-else-if="call.note" class="text-xs text-muted truncate">{{ call.note }}</span>
      </div>
    </div>
    <div class="band hide-narrow" :title="t('calls.bandHint')">
      <div class="band-bar" :style="{left: band.left + '%', width: band.width + '%'}"></div>
    </div>
    <div class="tabular text-sm text-right hide-narrow">{{ started }}</div>
    <div class="tabular text-sm text-right">{{ formatDuration(minutes) }}</div>
    <div class="tabular text-sm text-right">{{ call.members.length }}</div>
  </div>
</template>

<style scoped>
.call-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 62px 52px;
  gap: 12px;
  align-items: center;
  padding: 11px 18px;
  border-top: 1px solid var(--c-hairline);
  cursor: pointer;
}

.call-row:hover {
  background: var(--c-hairline);
}

.call-row.aborted {
  background: var(--c-signal-soft);
  box-shadow: inset 3px 0 0 var(--c-signal);
}

.band {
  position: relative;
  height: 8px;
  background: var(--c-band-track);
  border-radius: 1px;
}

.band-bar {
  position: absolute;
  top: 0;
  bottom: 0;
  min-width: 2px;
  background: var(--c-band);
  border-radius: 1px;
}

.call-row.aborted .band-bar {
  background: var(--c-signal);
}

@media (min-width: 900px) {
  .call-row, .head-row {
    grid-template-columns: minmax(0, 1fr) 190px 62px 62px 52px;
    gap: 16px;
  }
}

.hide-narrow {
  display: none;
}

@media (min-width: 900px) {
  .hide-narrow {
    display: block;
  }

  .band.hide-narrow {
    display: block;
  }
}
</style>
