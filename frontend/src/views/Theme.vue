<script setup lang="ts">
import ConfirmButton from "../components/base/buttons/derivates/ConfirmButton.vue";
import ErrorButton from "../components/base/buttons/derivates/ErrorButton.vue";
import InfoButton from "../components/base/buttons/derivates/InfoButton.vue";
import SuccessButton from "../components/base/buttons/derivates/SuccessButton.vue";
import WarningButton from "../components/base/buttons/derivates/WarningButton.vue";
import {t} from "../i18n";
</script>

<template>
  <ConfirmButton>{{ t('theme.confirm') }}</ConfirmButton>
  <ErrorButton>{{ t('theme.error') }}</ErrorButton>
  <InfoButton>{{ t('theme.info') }}</InfoButton>
  <SuccessButton>{{ t('theme.success') }}</SuccessButton>
  <WarningButton>{{ t('theme.warning') }}</WarningButton>
</template>

<style scoped>

</style>