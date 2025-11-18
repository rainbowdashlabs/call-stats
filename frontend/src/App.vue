<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import ErrorPopup from './components/base/ErrorPopup.vue'
</script>

<template>
  <div class="page">
    <header class="header">
      <div class="header-inner">
        <nav class="nav">
          <RouterLink to="/calls">Calls</RouterLink>
          <RouterLink to="/exercise">Exercise</RouterLink>
          <RouterLink to="/youth">Youth</RouterLink>
          <RouterLink to="/members">Members</RouterLink>
        </nav>
      </div>
    </header>

    <div class="app">
      <main class="main">
        <RouterView />
      </main>
    </div>

    <ErrorPopup />

    <footer class="footer">
      <div class="footer-inner">
        <p>© {{ new Date().getFullYear() }} CallStats. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Layout container to push footer to bottom when content is short */
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Content container grows to fill remaining space */
.app { max-width: 960px; margin: 0 auto; padding-left: 1rem; padding-right: 1rem; flex: 1 0 auto; width: 100%; }

/* Top header bar */
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  width: 100%;
  background: rgba(10, 10, 10, 0.85);
  backdrop-filter: saturate(180%) blur(8px);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 1px 2px rgba(0,0,0,0.6);
}

/* header content width aligns with page width */
.header-inner {
  max-width: 960px;
  margin: 0 auto;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Navigation buttons with orange accents */
.nav { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.5rem; width: 100%; }
.nav a { display: block; text-align: center; padding: 0.5rem 0.75rem; border: 1px solid rgba(255,255,255,0.12); border-radius: 0.5rem; background: rgba(255,255,255,0.03); color: inherit; text-decoration: none; transition: background-color 0.2s, border-color 0.2s, transform 0.05s; }
.nav a:hover { background: rgba(249,115,22,0.12); border-color: rgba(249,115,22,0.6); }
.nav a:active { transform: translateY(1px); }
.nav a:focus-visible { outline: 3px solid rgba(249,115,22,0.6); outline-offset: 2px; }
.nav a.router-link-active { font-weight: 700; background: rgba(249,115,22,0.18); border-color: rgba(249,115,22,0.9); }

/* Footer styles: normal flow at the end; sits at bottom when page is short */
.footer {
  width: 100%;
  background: rgba(10, 10, 10, 0.8);
  backdrop-filter: saturate(180%) blur(6px);
  border-top: 1px solid rgba(255,255,255,0.08);
}
.footer-inner {
  max-width: 960px;
  margin: 0 auto;
  padding: 0.75rem 1rem;
  color: rgba(255,255,255,0.7);
  font-size: 0.925rem;
}

.main { padding-top: 1rem; }
</style>
