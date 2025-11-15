<script setup lang="ts">
import router from "../router";
import CreateCall from "../components/calls/create/CreateCall.vue";
import ConfirmButton from "../components/base/buttons/derivates/ConfirmButton.vue";
</script>

<template>
  <section>
    <ConfirmButton @click="router.push({path: '/calls/subjects'})">Subjects</ConfirmButton>

    <CreateCall/>
  </section>
</template>
