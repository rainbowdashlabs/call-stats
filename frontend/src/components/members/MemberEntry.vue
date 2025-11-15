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

function edit() {
  router.push({path: `/member/${props.member.id!}`})
}
</script>

<template>
  <div class="flex gap-2">
    <div>
      {{ member.id! }}
    </div>
    <div class="flex-grow">
      {{ member.name }}
    </div>
    <div v-if="member.active_until">
      till {{ member.active_until }}
    </div>
    <div v-else>
      Aktiv
    </div>
    <div @click="edit" style="cursor: pointer">✏️</div>
  </div>
</template>

<style scoped>

</style>