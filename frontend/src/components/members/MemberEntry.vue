<script setup lang="ts">
import type {PropType} from "vue";
import type {Member} from "../../interfaces/Member.ts";
import router from "../../router";

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
      <span v-if="member.retired">bis {{ new Date((member.retired as number) * 1000).toLocaleDateString() }}</span>
      <span v-else>Aktiv</span>
    </div>
    <div>✏️</div>
  </div>
</template>

<style scoped>

</style>