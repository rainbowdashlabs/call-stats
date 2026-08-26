<script setup lang="ts">
import {ref} from "vue";
import {login} from "../api/auth.ts";
import {setAuth} from "../auth.ts";
import router from "../router";
import {brigadeName} from '../api/config'


import {t} from "../i18n";

/** A week of real-looking turnouts, drawn on the same 24-hour track the app uses everywhere. */
const week = [
  {label: 'Mo', bars: [{left: 38, width: 4, signal: false}]},
  {label: 'Di', bars: [{left: 8, width: 3, signal: false}, {left: 61, width: 7, signal: false}]},
  {label: 'Mi', bars: [{left: 74, width: 5, signal: false}]},
  {label: 'Do', bars: [{left: 26, width: 2, signal: true}, {left: 55, width: 11, signal: false}]},
  {label: 'Fr', bars: [{left: 47, width: 6, signal: false}]},
  {label: 'Sa', bars: [{left: 13, width: 9, signal: false}, {left: 80, width: 4, signal: false}]},
  {label: 'So', bars: [{left: 66, width: 3, signal: false}]}
]

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  if (!username.value || !password.value) return
  error.value = ''
  loading.value = true
  try {
    const response = await login(username.value, password.value)
    setAuth(response.token, response.role, username.value)
    await router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('login.failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login">
    <aside class="login-panel">
      <div class="login-mark">
        <span class="headline text-2xl tracking-wide uppercase">CallStats</span>
        <span v-if="brigadeName" class="panel-label mt-1">{{ brigadeName }}</span>
      </div>

      <div>
        <p class="login-claim">{{ t('login.claim') }}</p>
        <div class="week" aria-hidden="true">
          <div v-for="day in week" :key="day.label" class="week-row">
            <span class="panel-label w-6">{{ day.label }}</span>
            <div class="week-track">
              <div v-for="(bar, i) in day.bars" :key="i" class="week-bar"
                   :class="{signal: bar.signal}" :style="{left: bar.left + '%', width: bar.width + '%'}"></div>
            </div>
          </div>
          <div class="week-scale">
            <span v-for="hour in [0, 6, 12, 18, 24]" :key="hour" class="panel-label">{{ hour }}</span>
          </div>
        </div>
      </div>
    </aside>

    <form class="login-form" @submit.prevent="submit">
      <div class="eyebrow">{{ t('login.eyebrow') }}</div>
      <h1 class="headline text-3xl mt-1 mb-6">{{ t('login.title') }}</h1>

      <div v-if="error" class="login-error">{{ error }}</div>

      <label class="flex flex-col gap-2 mb-4">
        <span class="label">{{ t('login.user') }}</span>
        <input type="text" v-model="username" autocomplete="username" class="field"/>
      </label>
      <label class="flex flex-col gap-2 mb-6">
        <span class="label">{{ t('login.password') }}</span>
        <input type="password" v-model="password" autocomplete="current-password" class="field"/>
      </label>

      <button type="submit" class="login-submit" :disabled="loading || !username || !password">
        {{ loading ? t('common.loading') : t('login.submit') }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.login {
  flex-grow: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
}

@media (min-width: 900px) {
  .login {
    grid-template-columns: 1.05fr 1fr;
  }
}

.login-panel {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  gap: 48px;
  padding: 46px 48px;
  background: #10141a;
  color: #f4f6f8;
  border-top: 3px solid var(--c-signal);
}

@media (min-width: 900px) {
  .login-panel {
    display: flex;
  }
}

.login-mark {
  display: flex;
  flex-direction: column;
}

.panel-label {
  font-family: var(--font-condensed);
  font-weight: 600;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #8a94a2;
}

.login-claim {
  font-family: var(--font-condensed);
  font-weight: 600;
  font-size: 38px;
  line-height: 1.12;
  letter-spacing: 0.01em;
  max-width: 15ch;
  margin: 0 0 34px;
}

.week {
  display: flex;
  flex-direction: column;
  gap: 7px;
  max-width: 30rem;
}

.week-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.week-track {
  position: relative;
  flex-grow: 1;
  height: 7px;
  background: #1c222b;
}

.week-bar {
  position: absolute;
  top: 0;
  bottom: 0;
  background: #f4f6f8;
}

.week-bar.signal {
  background: var(--c-signal);
}

.week-scale {
  display: flex;
  justify-content: space-between;
  padding-left: 36px;
  margin-top: 3px;
}

.login-form {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px;
  max-width: 25rem;
  width: 100%;
  margin: 0 auto;
}

.login-error {
  margin-bottom: 18px;
  padding: 10px 12px;
  border: 1px solid var(--c-signal);
  border-left-width: 3px;
  border-radius: var(--radius-control);
  background: var(--c-signal-soft);
  color: var(--c-signal-ink);
  font-size: 14px;
}

.login-submit {
  height: 42px;
  border: 1px solid var(--c-action);
  border-radius: var(--radius-control);
  background: var(--c-action);
  color: var(--c-action-ink);
  font-family: var(--font-condensed);
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
}

.login-submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
