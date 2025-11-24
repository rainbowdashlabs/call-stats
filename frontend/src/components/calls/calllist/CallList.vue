<script setup lang="ts">

import {listCalls} from "../../../api/calls.ts";
import {useRoute} from "vue-router";
import {onMounted, ref, watch} from "vue";
import type {FullCall} from "../../../interfaces/Call.ts";
import router from "../../../router";
import CallEntry from "./CallEntry.vue";
import Navigation from "../../base/pagination/Navigation.vue";

const route = useRoute()
const page = ref<number>(Number(route.query.page) || 1)
const pageSize = ref(Number(route.query.pageSize) || 20)
const pageContent = ref<FullCall[]>([])
const pages = ref(1)

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
  let result = await listCalls(page.value, pageSize.value)
  pageContent.value = result.entries
  page.value = result.page
  pages.value = result.pages
}

defineExpose()

onMounted(load)

</script>

<template>


  <div class="flex justify-evenly">
    <div class="text-2xl">
      Alarme
    </div>
    <div class="flex justify-end">
      <div class="mr-2 content-center">Einträge pro Seite:</div>
      <select v-model="pageSize" @change="load">
        <option v-for="i in [5,10,20,50,100]" :value="i">{{ i }}</option>
      </select>
    </div>
  </div>

  <div class="border-2 rounded-2xl border-accent grid grid-cols-1 gap-2 p-2 mt-2 mb-2">
    <div class="grid grid-cols-5 gap-2 highlight rounded-2xl" @click="load" style="cursor: pointer">
      <div>Stichwort</div>
      <div>Start</div>
      <div>Ende</div>
      <div>Stärke</div>
      <div>Meta</div>
    </div>
    <CallEntry v-for="call in pageContent" :call="call"/>
  </div>

  <Navigation :pages="pages" :model-value="page"/>

</template>

<style scoped>
SimpleButton.hoverable:hover{
  background-color: var(--color-accent-secondary);
}
div.hoverable:hover {
  background-color: var(--color-accent-secondary);
}

div.chosen {
  background-color: var(--color-accent);
}

</style>