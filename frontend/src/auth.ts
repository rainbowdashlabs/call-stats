import {reactive} from "vue";

export interface AuthState {
    token: string | null
    role: string | null
    username: string | null
}

const STORAGE_KEY = 'callstats_auth'

function loadFromStorage(): AuthState {
    try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (raw) return JSON.parse(raw)
    } catch { /* ignore */ }
    return {token: null, role: null, username: null}
}

export const auth = reactive<AuthState>(loadFromStorage())

export function setAuth(token: string, role: string, username: string) {
    auth.token = token
    auth.role = role
    auth.username = username
    localStorage.setItem(STORAGE_KEY, JSON.stringify({token, role, username}))
}

export function clearAuth() {
    auth.token = null
    auth.role = null
    auth.username = null
    localStorage.removeItem(STORAGE_KEY)
}

export function isAuthenticated(): boolean {
    return !!auth.token
}

export function isAdmin(): boolean {
    return auth.role === 'admin'
}
