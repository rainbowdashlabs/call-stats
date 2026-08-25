<script setup lang="ts">
import router from "../router";
import {t} from "../i18n";
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 mt-10">
    <h1 class="text-4xl">404</h1>
    <p>{{ t('notFound.message') }}</p>
    <button class="bg-accent text-white p-2 rounded-md" @click="router.push('/')">{{ t('notFound.home') }}</button>
  </div>
</template>
