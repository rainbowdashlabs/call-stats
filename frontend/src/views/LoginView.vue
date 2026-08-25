<script setup lang="ts">
import {ref} from "vue";
import {login} from "../api/auth.ts";
import {setAuth} from "../auth.ts";
import router from "../router";
import {t} from "../i18n";

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
  <div class="min-h-screen flex items-center justify-center">
    <div class="bg-gray-800 p-8 rounded-lg w-full max-w-sm">
      <h1 class="text-2xl font-bold mb-6 text-center">{{ t('login.title') }}</h1>

      <div v-if="error" class="bg-red-900 text-white p-2 rounded mb-4 text-sm">{{ error }}</div>

      <form @submit.prevent="submit" class="flex flex-col gap-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">{{ t('login.user') }}</label>
          <input type="text" v-model="username" autocomplete="username"
                 class="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-orange-400 outline-none"/>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">{{ t('login.password') }}</label>
          <input type="password" v-model="password" autocomplete="current-password"
                 class="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-orange-400 outline-none"/>
        </div>
        <button type="submit" :disabled="loading || !username || !password"
                class="bg-orange-500 text-white py-2 rounded font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-orange-600 transition-colors">
          {{ loading ? t('common.loading') : t('login.submit') }}
        </button>
      </form>
    </div>
  </div>
</template>
