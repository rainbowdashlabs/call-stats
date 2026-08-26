<script setup lang="ts">
import CreateYouthExercise from "../components/youthexercise/CreateYouthExercise.vue";
import YouthExerciseList from "../components/youthexercise/YouthExerciseList.vue";
import {t} from '../i18n';
</script>

<template>
  <section class="flex flex-col gap-6">
    <header>
      <div class="eyebrow">{{ t('youth.eyebrow') }}</div>
      <h1 class="headline text-4xl mt-1">{{ t('youth.title') }}</h1>
    </header>
    <CreateYouthExercise/>
    <YouthExerciseList/>
  </section>
</template>
