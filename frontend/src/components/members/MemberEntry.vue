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
  <div class="grid grid-cols-6">
    <div class="">
      {{ member.id! }}
    </div>
    <div class="col-span-3">
      {{ member.name }}
    </div>
    <div class="">
      <div v-if="member.retired">
        bis {{ member.retired }}
      </div>
      <div v-else>
        Aktiv
      </div>
    </div>
    <div @click="edit" class="" style="cursor: pointer">✏️</div>
  </div>
</template>

<style scoped>

</style>