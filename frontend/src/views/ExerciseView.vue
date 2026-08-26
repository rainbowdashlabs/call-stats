<script setup lang="ts">
import CreateExercise from "../components/exercise/CreateExercise.vue";
import ExerciseList from "../components/exercise/ExerciseList.vue";
import {t} from '../i18n';
</script>

<template>
  <section class="flex flex-col gap-6">
    <header>
      <div class="eyebrow">{{ t('exercises.eyebrow') }}</div>
      <h1 class="headline text-4xl mt-1">{{ t('exercises.title') }}</h1>
    </header>
    <CreateExercise/>
    <ExerciseList/>
  </section>
</template>
