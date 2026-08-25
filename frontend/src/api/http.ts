import axios, {type AxiosInstance} from 'axios'
import {auth, clearAuth} from '../auth'

// Resolve API base URL with the following priority:
// 1) window.__API_BASE_URL__ (runtime override)
// 2) import.meta.env.VITE_API_BASE_URL (build-time env)
// 3) fallback '/api'

declare global {
    interface Window {
        __API_BASE_URL__?: string
        setApiBaseUrl?: (url: string) => void
    }
}

let baseURL: string =
    (typeof window !== 'undefined' && window.__API_BASE_URL__) ||
    import.meta.env?.VITE_API_BASE_URL ||
    ''

function createClient(): AxiosInstance {
    const instance = axios.create({
        baseURL,
        headers: {
            'Content-Type': 'application/json',
        },
    })

    instance.interceptors.request.use((config) => {
        if (auth.token) {
            config.headers.Authorization = `Bearer ${auth.token}`
        }
        return config
    })

    instance.interceptors.response.use(
        (response) => response,
        (error) => {
            if (error.response?.status === 401 && window.location.pathname !== '/login') {
                clearAuth()
                window.location.href = '/login'
            }
            return Promise.reject(error)
        }
    )

    return instance
}

let client: AxiosInstance = createClient()

export function getHttpClient(): AxiosInstance {
    return client
}

export function setApiBaseUrl(url: string) {
    if (!url || typeof url !== 'string') return
    baseURL = url
    client = createClient()
}

// Expose a global setter so hosts can inject from outside the app if needed
if (typeof window !== 'undefined') {
    window.setApiBaseUrl = setApiBaseUrl
}
