import { PUBLIC_API_BASE } from '$env/static/public';

async function request(path: string, options: RequestInit = {}) {
    const res = await fetch(`${PUBLIC_API_BASE}${path}`, {
        credentials: 'include',
        ...options
    });

    let data: any = null;
    try {
        data = await res.json();
    } catch {}

    if (!res.ok) {
        const message = data?.detail || data?.error || 'Request failed';
        throw new Error(message);
    }

    return data;
}

export const api = {
    login: (email: string, password: string) =>
        request('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        }),

    register: (payload: any) =>
        request('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }),

    me: () => request('/auth/me'),

    changePassword: (current_password: string, new_password: string) =>
        request('/auth/change-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ current_password, new_password })
        }),

    history: (page = 1, page_size = 10) =>
        request(`/auth/history?page=${page}&page_size=${page_size}`),

    analyzeXray: (file: File) => {
        const form = new FormData();
        form.append('file', file);
        return request('/analyze/xray', { method: 'POST', body: form });
    },

    analyzeCT: (file: File) => {
        const form = new FormData();
        form.append('file', file);
        return request('/analyze/ct', { method: 'POST', body: form });
    },

    health: () => request('/health')
};
