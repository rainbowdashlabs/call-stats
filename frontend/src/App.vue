<script setup lang="ts">
import Header from "./components/header/Header.vue";
import Footer from "./components/footer/Footer.vue";
</script>

<template>
  <div class="w-screen width min-h-screen">
    <div class="flex flex-col min-h-screen justify-between">
      <Header/>
      <div>
        <RouterView/>
      </div>
      <Footer/>
    </div>
  </div>
</template>

<style scoped>
.width {
  max-width: 100%;
}

.height {
  min-height: 100vh;
}
</style>
