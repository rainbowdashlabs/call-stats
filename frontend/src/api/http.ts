import axios, {type AxiosInstance} from 'axios'

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
    '/api'

console.log("Base: " + baseURL)
console.log("Base: " + import.meta.env.BASE_URL)
console.log("Base: " + import.meta.env.VITE_API_BASE_URL)

let client: AxiosInstance = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
})

export function getHttpClient(): AxiosInstance {
    return client
}

export function setApiBaseUrl(url: string) {
    if (!url || typeof url !== 'string') return
    baseURL = url
    client = axios.create({
        baseURL,
        headers: {
            'Content-Type': 'application/json',
        },
    })
}

// Expose a global setter so hosts can inject from outside the app if needed
if (typeof window !== 'undefined') {
    window.setApiBaseUrl = setApiBaseUrl
}
