import { defineStore } from 'pinia'
import { ref } from 'vue'
import { convex } from '../lib/convex'
import { api } from '../../../convex/_generated/api'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(JSON.parse(localStorage.getItem('convex_user') || 'null'))

    function setUser(userData) {
        user.value = userData
        localStorage.setItem('convex_user', JSON.stringify(userData))
    }

    function logout() {
        user.value = null
        localStorage.removeItem('convex_user')
    }

    async function login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const res = await fetch('/api/auth/login', {
            method: 'POST',
            body: formData
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Login failed');
        }

        const data = await res.json();
        setUser({ ...data.user, token: data.token });
        return data.user;
    }

    return { user, setUser, logout, login }
})
