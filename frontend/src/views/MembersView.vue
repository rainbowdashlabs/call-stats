<script setup lang="ts">

import {onMounted, ref} from "vue";
import type {Member} from "../interfaces/Member.ts";
import {listMembers} from "../api/members.ts";
import MemberEntry from "../components/members/MemberEntry.vue";

const members = ref<Member[]>([])

async function load() {
  members.value = await listMembers()
}

onMounted(load)

</script>

<template>
  <MemberEntry v-for="member in members" :member="member"/>
</template>
