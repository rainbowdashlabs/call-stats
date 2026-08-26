<script setup lang="ts">
import router from "../router";
import CreateCall from "../components/calls/create/CreateCall.vue";
import StandardButton from "../components/base/buttons/StandardButton.vue";
import CallList from "../components/calls/calllist/CallList.vue";
import {isAdmin} from "../auth.ts";
import {t} from "../i18n";
</script>

<template>
  <section class="flex flex-col gap-6">
    <header class="flex items-end justify-between gap-6">
      <div>
        <div class="eyebrow">{{ t('calls.eyebrow') }}</div>
        <h1 class="headline text-4xl mt-1">{{ t('calls.title') }}</h1>
      </div>
      <StandardButton v-if="isAdmin()" @click="router.push({path: '/calls/subjects'})">
        {{ t('subjects.title') }}
      </StandardButton>
    </header>

    <CreateCall v-if="isAdmin()"/>
    <CallList/>
  </section>
</template>
