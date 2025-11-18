<script setup lang="ts">

import {FontAwesomeIcon} from "@fortawesome/vue-fontawesome";
import SimpleButton from "../buttons/SimpleButton.vue";

const props = defineProps({
  pages: {
    type: Number,
    required: true
  }
})

const page = defineModel({
  type: Number,
  required: true
})

</script>

<template>
  <div class="flex justify-center">
    <SimpleButton @click="page = Math.max(page  - 1, 1)" class="border-2 border-accent w-8 hoverable">
      <font-awesome-icon icon="fa-solid fa-arrow-left"/>
    </SimpleButton>
    <div v-for="num in props.pages" class="hoverable border-2 border-accent w-8">
      <div v-if="num === page" class="chosen">
        {{ num }}
      </div>
      <div v-else @click="page = num" class="cursor-pointer">
        {{ num }}
      </div>
    </div>
    <SimpleButton @click="page = Math.min(page + 1, props.pages)" class="border-2 border-accent w-8 hoverable">
      <font-awesome-icon icon="fa-solid fa-arrow-right"/>
    </SimpleButton>
  </div>

</template>

<style scoped>

</style>