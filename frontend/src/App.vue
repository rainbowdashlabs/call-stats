<script setup lang="ts">
import {computed} from 'vue'
import {RouterLink, RouterView, useRoute} from 'vue-router'
import ErrorPopup from './components/base/ErrorPopup.vue'
import SuccessPopup from './components/base/SuccessPopup.vue'
import {auth, clearAuth, isAdmin, isAuthenticated} from './auth'
import router from './router'
import {t} from './i18n'
import {brigadeName} from './api/config'
import {activeTheme, toggleTheme} from './theme'

const route = useRoute()

/** Statistics and the deck ask for the full width; everything else reads better in a column. */
const contentWidth = computed(() => route.meta.wide ? 'max-w-[1560px]' : 'max-w-[1180px]')

function logout() {
  clearAuth()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-page text-ink">
    <header v-if="isAuthenticated()" class="bg-surface border-b border-rule">
      <div class="mx-auto w-full px-4 md:px-6 py-2 md:h-15 flex flex-wrap items-center gap-x-6 gap-y-2"
           :class="contentWidth">
        <RouterLink to="/calls" class="flex items-baseline gap-2 shrink-0 text-ink hover:text-ink">
          <span class="font-condensed font-bold text-xl tracking-wide uppercase">CallStats</span>
          <span v-if="brigadeName" class="label hidden sm:inline">{{ brigadeName }}</span>
        </RouterLink>

        <nav class="flex flex-wrap gap-x-5 gap-y-1 grow order-3 md:order-none w-full md:w-auto">
          <RouterLink to="/calls" class="nav-link">{{ t('nav.calls') }}</RouterLink>
          <RouterLink v-if="isAdmin()" to="/exercise" class="nav-link">{{ t('nav.exercises') }}</RouterLink>
          <RouterLink v-if="isAdmin()" to="/youth" class="nav-link">{{ t('nav.youth') }}</RouterLink>
          <RouterLink v-if="isAdmin()" to="/members" class="nav-link">{{ t('nav.members') }}</RouterLink>
          <RouterLink to="/statistics" class="nav-link">{{ t('nav.statistics') }}</RouterLink>
        </nav>

        <div class="flex items-center gap-4 shrink-0">
          <button type="button" class="icon-button" :title="t('theme.toggle')" @click="toggleTheme">
            <font-awesome-icon :icon="activeTheme() === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon'"/>
          </button>
          <span class="tabular text-[13px] text-muted">{{ auth.username }}</span>
          <button type="button" class="icon-button" :title="t('login.logout')" @click="logout">
            <font-awesome-icon icon="fa-solid fa-power-off"/>
          </button>
        </div>
      </div>
      <div class="h-[3px] bg-signal"></div>
    </header>

    <main class="grow flex flex-col" :class="isAuthenticated() ? `mx-auto w-full ${contentWidth} px-4 md:px-6 py-6 md:py-7` : ''">
      <RouterView/>
    </main>

    <ErrorPopup/>
    <SuccessPopup/>

    <footer v-if="isAuthenticated()" class="border-t border-rule bg-surface">
      <div class="mx-auto w-full px-4 md:px-6 py-3 label" :class="contentWidth">
        {{ t('app.copyright', {year: new Date().getFullYear()}) }}
      </div>
    </footer>
  </div>
</template>

<style scoped>
.nav-link {
  color: var(--c-muted);
  font-size: 15px;
  padding-bottom: 3px;
  border-bottom: 2px solid transparent;
  transition: color 0.15s;
}

.nav-link:hover {
  color: var(--c-ink);
}

.nav-link.router-link-active {
  color: var(--c-ink);
  font-weight: 600;
  border-bottom-color: var(--c-signal);
}

.icon-button {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-control);
  background: transparent;
  color: var(--c-muted);
  cursor: pointer;
  padding: 0;
}

.icon-button:hover {
  color: var(--c-ink);
  background: var(--c-raised);
}
</style>
