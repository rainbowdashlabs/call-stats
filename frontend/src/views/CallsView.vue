<script setup lang="ts">
import router from "../router";
import CreateCall from "../components/calls/create/CreateCall.vue";
</script>

<template>
  <section>
    <button @click="router.push({path: '/calls/subjects'}) ">Subjects</button>

    <CreateCall/>
  </section>
</template>
