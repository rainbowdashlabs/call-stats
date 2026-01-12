<script setup lang="ts">

import {FontAwesomeIcon} from "@fortawesome/vue-fontawesome";
import SimpleButton from "../buttons/SimpleButton.vue";
import {watch} from "vue";

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

const emit = defineEmits(["change"])

function pageList() {
  const total = props.pages;
  const current = page.value;
  const range: (number | string)[] = [];

  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= current - 2 && i <= current + 2)) range.push(i);
  }

  const withDots: (number | string)[] = [];
  let lastNum: number | undefined;

  for (const i of range) {
    if (typeof i === 'number') {
      if (lastNum !== undefined) {
        if (i - lastNum === 2) {
          withDots.push(lastNum + 1);
        } else if (i - lastNum > 2) {
          withDots.push("...");
        }
      }
      withDots.push(i);
      lastNum = i;
    }
  }

  return withDots;
}

watch(page, () => {
  emit("change", page.value)
})

</script>

<template>
  <div class="flex justify-center">
    <SimpleButton @click="page = Math.max(page  - 1, 1)" class="border-2 border-accent w-8 hoverable">
      <font-awesome-icon icon="fa-solid fa-arrow-left"/>
    </SimpleButton>
    <div v-for="num in pageList()" :key="num" class="flex">
      <div v-if="num === '...'" class="w-8 flex items-center justify-center">
        {{ num }}
      </div>
      <div v-else
           @click="page = num as number"
           class="hoverable border-2 border-accent w-8 cursor-pointer flex items-center justify-center"
           :class="{ 'bg-blue-900': num === page }">
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