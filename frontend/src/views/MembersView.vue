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
  <section class="flex flex-col gap-6">
    <header>
      <div class="eyebrow">{{ t('members.eyebrow') }}</div>
      <h1 class="headline text-4xl mt-1">{{ t('members.title') }}</h1>
    </header>

    <div v-if="isAdmin()" class="card p-5 flex flex-col gap-3">
      <span class="label">{{ t('members.newMember') }}</span>
      <div class="flex gap-3">
        <input type="text" class="field" style="max-width: 22rem" :placeholder="t('common.name')" v-model="name">
        <ConfirmButton @click="create" :disabled="!canCreate">
          <font-awesome-icon icon="fa-solid fa-plus"/>
          {{ t('common.create') }}
        </ConfirmButton>
      </div>
    </div>

    <label class="flex items-center gap-2 w-fit cursor-pointer">
      <input type="checkbox" v-model="show_retired">
      <span class="label">{{ t('members.showRetired') }}</span>
    </label>

    <div class="card">
      <div class="member-head">
        <span class="label">{{ t('common.id') }}</span>
        <span class="label">{{ t('common.name') }}</span>
        <span class="label text-right">{{ t('members.status') }}</span>
      </div>
      <div v-if="loading" class="p-8 text-center text-muted">{{ t('common.loading') }}</div>
      <div v-else-if="members.length === 0" class="p-8 text-center text-muted">{{ t('members.empty') }}</div>
      <MemberEntry v-else v-for="member in members" :key="member.id" :member="member"/>
    </div>
  </section>
</template>

<style scoped>
.member-head {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr) 110px;
  gap: 10px;
  padding: 9px 18px;
  background: var(--c-raised);
}

@media (min-width: 700px) {
  .member-row, .member-head {
    grid-template-columns: 64px minmax(0, 1fr) 200px;
    gap: 16px;
  }
}
</style>
