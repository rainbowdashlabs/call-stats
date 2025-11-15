<script setup lang="ts">
import {onBeforeRouteUpdate, useRoute} from "vue-router";
import {onMounted, ref} from "vue";
import type {Member} from "../interfaces/Member.ts";
import {getMember} from "../api/member.ts";
import MemberQualifications from "../components/member/MemberQualifications.vue";

const member = ref<Member>()

let route = useRoute()

async function load(id: number | null = null) {
  if (!id) {
    id = Number(route.params.id)
  }
  member.value = await getMember(id)
}

onBeforeRouteUpdate(async (to, _) => await load(Number(to.params.id!)))

onMounted(load)
</script>

<template>
  <div>
    {{ member }}
  </div>
  <MemberQualifications v-if="member" :member="member"/>
</template>

<style scoped>

</style>