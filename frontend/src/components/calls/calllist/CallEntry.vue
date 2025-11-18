<script setup lang="ts">
import type {PropType} from "vue";
import type {FullCall} from "../../../interfaces/Call.ts";
import {formatDateTime} from "../../../scripts/datetime.ts";
import router from "../../../router";

const  props = defineProps({
  call: {
    type: Object as PropType<FullCall>,
    required: true
  }
})

async function load() {
  await router.push({name: "Call", params: {"id": props.call!.id}})
}
</script>

<template>
  <div class="grid grid-cols-5 gap-2 highlight rounded-2xl" @click="load" style="cursor: pointer">
    <div>{{ call.subjects.map(s => s.name).join(' + ') }}</div>
    <div>{{ formatDateTime(call.start as string) }}</div>
    <div>{{ formatDateTime(call.end as string) }}</div>
    <div>{{ call.members.length }}</div>
    <div>{{ call.abort_reason ? "⚠️" : "" }} {{ call.note ? "📝" : "" }}</div>
  </div>
</template>

<style scoped>
div.highlight:hover { background-color: #222; }

</style>