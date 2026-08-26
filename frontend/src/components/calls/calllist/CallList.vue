<script setup lang="ts">

import {listCalls} from "../../../api/calls.ts";
import {useRoute} from "vue-router";
import {onUnmounted, onMounted, ref, watch} from "vue";
import type {FullCall} from "../../../interfaces/Call.ts";
import router from "../../../router";
import CallEntry from "./CallEntry.vue";
import Navigation from "../../base/pagination/Navigation.vue";
import {bus} from "../../../events/bus.ts";
import {t} from "../../../i18n";

const route = useRoute()
const page = ref<number>(Number(route.query.page) || 1)
const pageSize = ref(Number(route.query.pageSize) || 20)
const pageContent = ref<FullCall[]>([])
const pages = ref(1)
const loading = ref(false)

watch(page, async (value, _) => await switchPage(value))
watch(pageSize, async () => {
  page.value = 1
  await switchPage(1)
})

async function switchPage(page: number) {
  await router.push({path: route.path, query: {page: page, pageSize: pageSize.value}})
  await load()
}

async function load() {
  loading.value = true
  try {
    let result = await listCalls(page.value, pageSize.value)
    pageContent.value = result.entries
    page.value = result.page
    pages.value = result.pages
  } finally {
    loading.value = false
  }
}

let stopListening: (() => void) | null = null

onMounted(() => {
  void load()
  stopListening = bus.on('call-created', () => {
    page.value = 1
    void load()
  })
})

onUnmounted(() => {
  stopListening?.()
  stopListening = null
})

</script>

<template>
  <section class="card">
    <div class="flex items-baseline justify-between px-5 pt-4 pb-3 border-b border-rule">
      <h2 class="headline text-xl">{{ t('calls.title') }}</h2>
      <label class="flex items-center gap-2">
        <span class="label">{{ t('common.entriesPerPage') }}</span>
        <select v-model="pageSize" class="field tabular" style="height: 30px; width: auto; padding: 0 6px;">
          <option v-for="i in [5,10,20,50,100]" :value="i">{{ i }}</option>
        </select>
      </label>
    </div>

    <div class="head-row">
      <span class="label">{{ t('common.subject') }}</span>
      <span class="label hide-narrow">{{ t('calls.band') }}</span>
      <span class="label text-right hide-narrow">{{ t('common.start') }}</span>
      <span class="label text-right">{{ t('common.duration') }}</span>
      <span class="label text-right">{{ t('calls.strength') }}</span>
    </div>

    <div v-if="loading" class="p-8 text-center text-muted">{{ t('common.loading') }}</div>
    <div v-else-if="pageContent.length === 0" class="p-8 text-center text-muted">{{ t('calls.empty') }}</div>
    <CallEntry v-else v-for="call in pageContent" :key="call.id" :call="call"/>

    <div class="px-5 py-3 border-t border-rule">
      <Navigation :pages="pages" v-model="page"/>
    </div>
  </section>
</template>

<style scoped>
.head-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 62px 52px;
  gap: 12px;
  padding: 9px 18px;
  background: var(--c-raised);
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
}
</style>
