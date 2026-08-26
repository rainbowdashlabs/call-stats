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
  <div class="member-row" @click="edit" role="button" tabindex="0" @keydown.enter="edit">
    <span class="tabular text-sm text-muted">{{ member.id }}</span>
    <span class="truncate font-medium">{{ member.name }}</span>
    <span class="text-right">
      <span v-if="member.retired" class="label">{{ t('members.until', {date: formatDate(member.retired!)}) }}</span>
      <span v-else class="label" style="color: var(--c-ink)">{{ t('members.active') }}</span>
    </span>
  </div>
</template>

<style scoped>
.member-row {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr) 110px;
  gap: 10px;
  align-items: center;
  padding: 11px 18px;
  border-top: 1px solid var(--c-hairline);
  cursor: pointer;
}

.member-row:hover {
  background: var(--c-hairline);
}

@media (min-width: 700px) {
  .member-row, .member-head {
    grid-template-columns: 64px minmax(0, 1fr) 200px;
    gap: 16px;
  }
}
</style>
