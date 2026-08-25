<script setup lang="ts">
import ButtonMultiSelectButton from "./buttonmultistelect/ButtonMultiSelectButton.vue";

defineProps<{
  options: any[]
  valueMapper: (item: any) => string
  keyMapper: (item: any) => any
}>()

const model = defineModel<any[]>({default: []})

function add(item: any) {
  if (!model.value.includes(item)) {
    model.value = [...model.value, item]
  }
}

function remove(item: any) {
  model.value = model.value.filter(v => v !== item)
}

function toggle(item: any, selected: boolean) {
  if (selected) add(item)
  else remove(item)
}
</script>

<template>
  <div class="grid grid-cols-4 gap-2">
    <ButtonMultiSelectButton
        v-for="item in options"
        :key="keyMapper(item)"
        :value="valueMapper(item)"
        :selected="model.includes(item)"
        @select="toggle(item, true)"
        @deselect="toggle(item, false)"/>
  </div>
</template>
