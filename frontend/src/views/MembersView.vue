<script setup lang="ts">

import {computed, onMounted, ref, watch} from "vue";
import type {Member} from "../interfaces/Member.ts";
import {createMember, listMembers} from "../api/members.ts";
import MemberEntry from "../components/members/MemberEntry.vue";
import ConfirmButton from "../components/base/buttons/derivates/ConfirmButton.vue";
import router from "../router";
import {isAdmin} from "../auth.ts";
import {t} from "../i18n";

const members = ref<Member[]>([])
const loading = ref(false)

const show_retired = ref(false)
const name = ref('')
const canCreate = computed(() => name.value.trim().length > 0)

watch(show_retired, () => load())

async function load() {
  loading.value = true
  try {
    members.value = await listMembers(!show_retired.value)
  } finally {
    loading.value = false
  }
}

async function create() {
  let newMember = await createMember({name: name.value!, retired: null})
  await router.push({path: `/member/${newMember.id!}`})
}

onMounted(load)

</script>

<template>
  <div>{{ t('members.title') }}</div>

  <div v-if="isAdmin()" class="flex gap-2">
    <input type="text" :placeholder="t('common.name')" v-model="name">
    <ConfirmButton @click="create" :disabled="!canCreate">{{ t('common.create') }}</ConfirmButton>
  </div>

  <div class="flex gap-2">
    {{ t('members.showRetired') }} <input type="checkbox" v-model="show_retired">
  </div>
  <div v-if="loading" class="p-4">{{ t('common.loading') }}</div>
  <div v-else-if="members.length === 0" class="p-4">{{ t('members.empty') }}</div>
  <MemberEntry v-else v-for="member in members" :member="member"/>
</template>
