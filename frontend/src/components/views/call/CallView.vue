<script setup lang="ts">

import {watch} from "vue";
import {useRoute} from "vue-router";

const route = useRoute()

watch(() => route.params.id,
    (newId, oldId) => {
      // TODO react to route change
    })
</script>

<template>
CallView {{ route.params.id }}
</template>

<style scoped>

</style>
