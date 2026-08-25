<script setup lang="ts">
import router from "../router";
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 mt-10">
    <h1 class="text-4xl">404</h1>
    <p>Seite nicht gefunden.</p>
    <button class="bg-accent text-white p-2 rounded-md" @click="router.push('/')">Zur Startseite</button>
  </div>
</template>
