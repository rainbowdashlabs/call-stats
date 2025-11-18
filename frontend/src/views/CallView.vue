<script setup lang="ts">
import {useRoute} from "vue-router";
import {computed, onMounted, ref} from "vue";
import {getCall, removeCall} from "../api/call.ts";
import type {FullCall} from "../interfaces/Call.ts";
import ErrorButton from "../components/base/buttons/derivates/ErrorButton.vue";
import router from "../router";
import {formatDateTime} from "../scripts/datetime.ts";

const route = useRoute()

const id: number = Number(route.params.id!)
const call = ref<FullCall | null>(null)

async function load() {
  call.value = await getCall(id)
}

async function remove() {
  await removeCall(id)
  await router.push({name: "Calls"})
}

const subjects = computed(() => {
  return call.value?.subjects.map(v => v.name).join(" + ")
})

const start = computed(() => {
  return call.value?.start ? formatDateTime(call.value.start as string) : ""
})

const end = computed(() => {
  return call.value?.end ? formatDateTime(call.value.end as string) : ""
})

const members = computed(() =>{
  return call.value?.members.map(v => v.name).join(", ")
})

onMounted(load)
</script>

<template>
  <div>
    <h1>{{ subjects }}</h1>

    <div>{{ end }} - {{ start }}</div>

    <div>{{members}}</div>

    <div v-if="call?.note">📝 {{ call?.note }}</div>

    <div v-if="call?.abort_reason">⚠️ {{ call?.abort_reason}}</div>

    <ErrorButton @click="remove">Delete</ErrorButton>
  </div>
</template>

<style scoped>

</style>