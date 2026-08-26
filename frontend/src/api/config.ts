import {ref} from 'vue'
import {getHttpClient} from './http'

const http = getHttpClient()

/** The brigade the installation belongs to, read from the server's BRIGADE_NAME. */
export const brigadeName = ref<string>(import.meta.env?.VITE_BRIGADE_NAME ?? '')

export async function loadConfig() {
    try {
        const {data} = await http.get<{ brigade_name: string }>('/api/config')
        if (data.brigade_name) brigadeName.value = data.brigade_name
    } catch { /* the header simply carries no brigade name */ }
}
