<script setup lang="ts">
import {ref} from 'vue'

interface Props {
  /**
   * Text to show when hovering the wrapper
   */
  hoverText: string
  /**
   * Optional position for the hover text
   */
  position?: 'top' | 'right' | 'bottom' | 'left'
}

withDefaults(defineProps<Props>(), {
  position: 'top',
})

const isHovered = ref(false)
</script>

<template>
  <div
      class="relative inline-block"
      @mouseenter="isHovered = true"
      @mouseleave="isHovered = false"
  >
    <!-- Whatever the consumer passes in -->
    <slot/>

    <!-- Hover text -->
    <transition name="fade">
      <div
          v-if="isHovered"
          class="absolute z-50 px-2 py-1 text-sm text-white bg-black rounded shadow"
          :class="{
          'bottom-full left-1/2 -translate-x-1/2 mb-1': position === 'top',
          'top-full left-1/2 -translate-x-1/2 mt-1': position === 'bottom',
          'left-full top-1/2 -translate-y-1/2 ml-1': position === 'right',
          'right-full top-1/2 -translate-y-1/2 mr-1': position === 'left',
        }"
      >
        {{ hoverText }}
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.12s ease-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>