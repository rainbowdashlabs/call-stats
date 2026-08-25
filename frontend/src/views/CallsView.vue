<script setup lang="ts">
import router from "../router";
import CreateCall from "../components/calls/create/CreateCall.vue";
import ConfirmButton from "../components/base/buttons/derivates/ConfirmButton.vue";
import CallList from "../components/calls/calllist/CallList.vue";
import {isAdmin} from "../auth.ts";
</script>

<template>
  <section>
    <template v-if="isAdmin()">
      <ConfirmButton @click="router.push({path: '/calls/subjects'})">Stichwörter</ConfirmButton>
      <CreateCall/>
    </template>

    <CallList/>
  </section>
</template>
