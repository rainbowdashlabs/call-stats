import axios from 'axios'

export interface LoginResponse {
    token: string
    role: string
}

export async function login(username: string, password: string): Promise<LoginResponse> {
    const {data} = await axios.post<LoginResponse>('/api/auth/login', {username, password})
    return data
}
