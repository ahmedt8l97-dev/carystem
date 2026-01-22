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
        // Simple hash for demo
        const msgBuffer = new TextEncoder().encode(password);
        const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const passwordHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

        const result = await convex.mutation(api.users.login, { username, passwordHash });
        if (result.error) throw new Error(result.error);

        setUser({ ...result.user, token: result.token });
        return result.user;
    }

    return { user, setUser, logout, login }
})
