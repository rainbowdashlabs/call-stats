<script setup lang="ts">

import {onMounted, ref, watch} from "vue";
import type {Member} from "../interfaces/Member.ts";
import {createMember, listMembers} from "../api/members.ts";
import MemberEntry from "../components/members/MemberEntry.vue";
import ConfirmButton from "../components/base/buttons/derivates/ConfirmButton.vue";
import router from "../router";

const members = ref<Member[]>([])

const show_retired = ref(false)
const name = ref('')

watch(show_retired, () => load())

async function load() {
  members.value = await listMembers(!show_retired.value)
}

async function create() {
  let newMember = await createMember({name: name.value!, retired: null})
  await router.push({path: `/member/${newMember.id!}`})
}

onMounted(load)

</script>

<template>
  <div>Members</div>

  <div class="flex gap-2">
    <input type="text" placeholder="name" v-model="name">
    <ConfirmButton @click="create">Create</ConfirmButton>
  </div>

  <div class="flex gap-2">
    Show retired: <input type="checkbox" v-model="show_retired">
  </div>
  <MemberEntry v-for="member in members" :member="member"/>
</template>
