<script setup lang="ts">
import {ref} from "vue";
import ConfirmButton from "../components/base/buttons/derivates/ConfirmButton.vue";
import ErrorButton from "../components/base/buttons/derivates/ErrorButton.vue";
import InfoButton from "../components/base/buttons/derivates/InfoButton.vue";
import SuccessButton from "../components/base/buttons/derivates/SuccessButton.vue";
import WarningButton from "../components/base/buttons/derivates/WarningButton.vue";

const colors = ref<string[]>(["bg-primary", "bg-secondary"])

function colorlist(): string[] {
  console.log(colors.value)
  return colors.value.map(c => c.replace('bg-', ''))
}
</script>

<template>
  <ConfirmButton>Confirm</ConfirmButton>
  <ErrorButton>Error</ErrorButton>
  <InfoButton>Info</InfoButton>
  <SuccessButton>Success</SuccessButton>
  <WarningButton>Warning</WarningButton>
</template>

<style scoped>

</style>