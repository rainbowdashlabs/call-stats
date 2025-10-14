<script setup lang="ts">
import {ref} from "vue";
import StandardButton from "../../base/buttons/StandardButton.vue";
import {type MultiSelectGroup, type MultiSelectItem} from "../../../interfaces/Subject.ts";

defineProps({
  group: {
    type: Object as () => MultiSelectGroup,
    required: true
  }
})

defineEmits<{
  (e: 'click', item: MultiSelectItem): void
}>()

const active = ref(false)
</script>

<template>
  <div>
    <StandardButton class="w-full bg-gray-200" @click="active = !active">{{ group.label }}</StandardButton>
    <div class="flex" v-if="active" v-for="item in group.items">
      <StandardButton class="w-full bg-blue-200" @click="_ => $emit('click', item)">{{
          item.label
        }}
      </StandardButton>
    </div>
  </div>
</template>

<style scoped>

</style>
