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

    async function checkAuth() {
        // Always return true since we disabled the login system
        if (!user.value) {
            setUser({
                username: "admin",
                name: "مدير النظام",
                role: "admin",
                token: "free_access"
            });
        }
        return true;
    }

    return { user, setUser, logout, checkAuth }
})
