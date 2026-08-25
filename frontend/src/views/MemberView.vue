<script setup lang="ts">
import {onBeforeRouteUpdate, useRoute} from "vue-router";
import {onMounted, ref} from "vue";
import type {Member} from "../interfaces/Member.ts";
import {getMember, updateMember} from "../api/member.ts";
import MemberQualifications from "../components/member/MemberQualifications.vue";
import MemberActivity from "../components/member/MemberActivity.vue";
import SimpleButton from "../components/base/buttons/SimpleButton.vue";
import {formatDate, parseDate, todayDate} from "../scripts/datetime.ts";
import Tooltip from "../components/base/Tooltip.vue";
import {isAdmin} from "../auth.ts";
import {t} from "../i18n";

const member = ref<Member>()

let route = useRoute()

const edit_name = ref(false)
const new_name = ref('')
const edit_retire = ref(false)
const retire_date = ref(todayDate())
const edit_joined = ref(false)
const joined_date = ref(todayDate())

async function load(id: number | null = null) {
  if (!id) {
    id = Number(route.params.id)
  }
  member.value = await getMember(id)
  new_name.value = member.value.name
}

async function updateName() {
  member.value!.name = new_name.value
  member.value = await updateMember(member.value!)
  edit_name.value = false
}

async function updateRetire() {
  member.value!.retired = parseDate(retire_date.value)
  member.value = await updateMember(member.value!)
  edit_retire.value = false
}

async function updateJoined() {
  member.value!.joined = parseDate(joined_date.value)
  member.value = await updateMember(member.value!)
  edit_joined.value = false
}

async function removeJoined() {
  member.value!.joined = null
  member.value = await updateMember(member.value!)
}

async function removeRetire() {
  member.value!.retired = null
  member.value = await updateMember(member.value!)
}

onBeforeRouteUpdate(async (to, _) => await load(Number(to.params.id!)))

onMounted(load)
</script>

<template>
  <div class="grid grid-cols-2 gap-2">
    <div class="flex justify-end">{{ t('common.id') }}</div>
    <div class="flex justify-start">{{ member?.id }}</div>

    <div class="flex justify-end">{{ t('common.name') }}</div>
    <div class="flex gap-2 justify-start">
      <div v-if="!edit_name" class="flex gap-2">
        <div>{{ member?.name }}</div>
        <SimpleButton v-if="isAdmin()" @click="edit_name = true">✏️</SimpleButton>
      </div>
      <div v-else class="flex gap-2">
        <input type="text" v-model="new_name"/>
        <SimpleButton @click="updateName">✔️</SimpleButton>
        <SimpleButton @click="edit_name = false">️❌</SimpleButton>
      </div>
    </div>

    <div class="flex justify-end">{{ t('members.joined') }}</div>
    <div class="flex justify-start gap-2">
      <div v-if="member?.joined" class="flex gap-2">
        {{ formatDate(member!.joined!) }}
        <Tooltip v-if="isAdmin()" :hoverText="t('members.removeJoined')">
          <SimpleButton @click="removeJoined">🗑️</SimpleButton>
        </Tooltip>
      </div>
      <div v-else-if="edit_joined" class="flex gap-2">
        <input type="date" v-model="joined_date">
        <SimpleButton @click="updateJoined">✔️</SimpleButton>
        <SimpleButton @click="edit_joined = false">❌</SimpleButton>
      </div>
      <div v-else class="flex gap-2">
        {{ t('members.joinedUnknown') }}
        <Tooltip v-if="isAdmin()" :hoverText="t('members.setJoined')">
          <SimpleButton @click="edit_joined = true">📅</SimpleButton>
        </Tooltip>
      </div>
    </div>

    <div class="flex justify-end">{{ t('members.retired') }}</div>
    <div class="flex justify-start gap-2">
      <div v-if="member?.retired" class="flex gap-2">
        {{ formatDate(member!.retired!) }}
        <Tooltip v-if="isAdmin()" :hoverText="t('members.removeRetirement')">
          <SimpleButton @click="removeRetire">🗑️</SimpleButton>
        </Tooltip>
      </div>
      <div v-else class="flex gap-2">
        <div v-if="edit_retire" class="flex gap-2">
          <input type="date" v-model="retire_date">
          <SimpleButton @click="updateRetire">✔️</SimpleButton>
          <SimpleButton @click="edit_retire = false">❌</SimpleButton>
        </div>
        <div v-else class="flex gap-2">
          {{ t('members.active') }}
          <Tooltip v-if="isAdmin()" :hoverText="t('members.retire')">
            <SimpleButton @click="edit_retire = true">🚪</SimpleButton>
          </Tooltip>
        </div>
      </div>
    </div>
  </div>
  <MemberQualifications v-if="member && isAdmin()" :member="member"/>
  <MemberActivity v-if="member" :member="member"/>
</template>

<style scoped>

</style>