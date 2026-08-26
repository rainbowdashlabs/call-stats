<script setup lang="ts">

import {FontAwesomeIcon} from "@fortawesome/vue-fontawesome";
import {watch} from "vue";
import {t} from "../../../i18n";

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
  <div class="pager">
    <button type="button" class="page-btn" :disabled="page <= 1" @click="page = Math.max(page - 1, 1)"
            :aria-label="t('common.previousPage')">
      <font-awesome-icon icon="fa-solid fa-arrow-left"/>
    </button>
    <template v-for="num in pageList()" :key="num">
      <span v-if="num === '...'" class="gap">…</span>
      <button v-else type="button" class="page-btn tabular" :class="{current: num === page}"
              @click="page = num as number">{{ num }}</button>
    </template>
    <button type="button" class="page-btn" :disabled="page >= props.pages"
            @click="page = Math.min(page + 1, props.pages)" :aria-label="t('common.nextPage')">
      <font-awesome-icon icon="fa-solid fa-arrow-right"/>
    </button>
  </div>
</template>

<style scoped>
.pager {
  display: flex;
  justify-content: center;
  gap: 6px;
}

.page-btn {
  min-width: 30px;
  height: 30px;
  padding: 0 7px;
  border: 1px solid var(--c-rule);
  border-radius: 3px;
  background: var(--c-surface);
  color: var(--c-ink);
  font-size: 13px;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: var(--c-raised);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn.current {
  background: var(--c-action);
  border-color: var(--c-action);
  color: var(--c-action-ink);
  font-weight: 600;
}

.gap {
  display: flex;
  align-items: center;
  padding: 0 3px;
  color: var(--c-faint);
}
</style>
