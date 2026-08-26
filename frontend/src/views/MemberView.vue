<script setup lang="ts">
import {onBeforeRouteUpdate, useRoute} from "vue-router";
import {onMounted, ref} from "vue";
import type {Member} from "../interfaces/Member.ts";
import {getMember, updateMember} from "../api/member.ts";
import MemberQualifications from "../components/member/MemberQualifications.vue";
import MemberActivity from "../components/member/MemberActivity.vue";
import SimpleButton from "../components/base/buttons/SimpleButton.vue";
import {formatDate, parseDate, todayDate} from "../scripts/datetime.ts";
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
  <section v-if="member" class="flex flex-col gap-6">
    <header class="flex items-start justify-between gap-6">
      <div class="min-w-0">
        <div class="eyebrow">{{ t('members.eyebrow') }} · <span class="tabular">{{ member.id }}</span></div>
        <div v-if="!edit_name" class="flex items-center gap-3 mt-1">
          <h1 class="headline text-4xl truncate">{{ member.name }}</h1>
          <SimpleButton v-if="isAdmin()" @click="edit_name = true" :aria-label="t('common.edit')">
            <font-awesome-icon icon="fa-solid fa-pen"/>
          </SimpleButton>
        </div>
        <div v-else class="flex items-center gap-2 mt-1">
          <input type="text" v-model="new_name" class="field" style="max-width: 20rem"/>
          <SimpleButton @click="updateName" :aria-label="t('common.save')">
            <font-awesome-icon icon="fa-solid fa-check"/>
          </SimpleButton>
          <SimpleButton @click="edit_name = false" :aria-label="t('common.cancel')">
            <font-awesome-icon icon="fa-solid fa-xmark"/>
          </SimpleButton>
        </div>
      </div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card p-4">
        <span class="label">{{ t('members.joined') }}</span>
        <div class="flex items-center gap-2 mt-2">
          <template v-if="member.joined">
            <span class="tabular text-lg">{{ formatDate(member.joined!) }}</span>
            <SimpleButton v-if="isAdmin()" @click="removeJoined" :aria-label="t('members.removeJoined')">
              <font-awesome-icon icon="fa-solid fa-trash"/>
            </SimpleButton>
          </template>
          <template v-else-if="edit_joined">
            <input type="date" v-model="joined_date" class="field" style="max-width: 12rem">
            <SimpleButton @click="updateJoined" :aria-label="t('common.save')">
              <font-awesome-icon icon="fa-solid fa-check"/>
            </SimpleButton>
            <SimpleButton @click="edit_joined = false" :aria-label="t('common.cancel')">
              <font-awesome-icon icon="fa-solid fa-xmark"/>
            </SimpleButton>
          </template>
          <template v-else>
            <span class="text-muted">{{ t('members.joinedUnknown') }}</span>
            <SimpleButton v-if="isAdmin()" @click="edit_joined = true" :aria-label="t('members.setJoined')">
              <font-awesome-icon icon="fa-solid fa-calendar-days"/>
            </SimpleButton>
          </template>
        </div>
      </div>

      <div class="card p-4">
        <span class="label">{{ t('members.retired') }}</span>
        <div class="flex items-center gap-2 mt-2">
          <template v-if="member.retired">
            <span class="tabular text-lg">{{ formatDate(member.retired!) }}</span>
            <SimpleButton v-if="isAdmin()" @click="removeRetire" :aria-label="t('members.removeRetirement')">
              <font-awesome-icon icon="fa-solid fa-rotate-left"/>
            </SimpleButton>
          </template>
          <template v-else-if="edit_retire">
            <input type="date" v-model="retire_date" class="field" style="max-width: 12rem">
            <SimpleButton @click="updateRetire" :aria-label="t('common.save')">
              <font-awesome-icon icon="fa-solid fa-check"/>
            </SimpleButton>
            <SimpleButton @click="edit_retire = false" :aria-label="t('common.cancel')">
              <font-awesome-icon icon="fa-solid fa-xmark"/>
            </SimpleButton>
          </template>
          <template v-else>
            <span class="text-lg">{{ t('members.active') }}</span>
            <SimpleButton v-if="isAdmin()" @click="edit_retire = true" :aria-label="t('members.retire')">
              <font-awesome-icon icon="fa-solid fa-right-from-bracket"/>
            </SimpleButton>
          </template>
        </div>
      </div>
    </div>

    <MemberQualifications v-if="isAdmin()" :member="member"/>
    <MemberActivity :member="member"/>
  </section>

  <div v-else class="p-10 text-center text-muted">{{ t('common.loading') }}</div>
</template>
