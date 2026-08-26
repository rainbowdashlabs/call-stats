<script setup lang="ts">
import router from "../router";
import {t} from "../i18n";
import ConfirmButton from '../components/base/buttons/derivates/ConfirmButton.vue';
</script>

<template>
  <section class="flex flex-col items-center justify-center gap-4 py-24 text-center">
    <div class="headline text-7xl">404</div>
    <p class="text-muted">{{ t('notFound.message') }}</p>
    <ConfirmButton @click="router.push('/')">{{ t('notFound.home') }}</ConfirmButton>
  </section>
</template>
