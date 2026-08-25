<script setup lang="ts">
import type {PropType} from "vue";
import type {Member} from "../../interfaces/Member.ts";
import router from "../../router";
import {formatDate} from "../../scripts/datetime.ts";
import {t} from "../../i18n";

const props = defineProps({
  member: {
    type: Object as PropType<Member>,
    required: true
  }
})

async function edit() {
  await router.push({path: `/member/${props.member.id!}`})
}
</script>

<template>
  <div class="grid grid-cols-6 py-1 hover:bg-gray-800 rounded cursor-pointer" @click="edit">
    <div>{{ member.id }}</div>
    <div class="col-span-3">{{ member.name }}</div>
    <div>
      <span v-if="member.retired">{{ t('members.until', { date: formatDate(member.retired as number) }) }}</span>
      <span v-else>{{ t('members.active') }}</span>
    </div>
    <div>✏️</div>
  </div>
</template>

<style scoped>

</style>