<script setup lang="ts">

</script>

<template>
  <div class="flex justify-evenly">
    <RouterLink :to="{name: 'home'}">Home</RouterLink>
    <RouterLink :to="{name: 'calls'}">Calls</RouterLink>
    <RouterLink :to="{name: 'exercises'}">Exercises</RouterLink>
    <RouterLink :to="{name: 'crew'}">Crew</RouterLink>
  </div>
</template>

<style scoped>

</style>
