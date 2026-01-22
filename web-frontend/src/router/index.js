import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Auth from '../views/Auth.vue'
import DashboardLayout from '../views/DashboardLayout.vue'
import DashboardHome from '../views/DashboardHome.vue'
import Inventory from '../views/Inventory.vue'
import AddProduct from '../views/AddProduct.vue'
import Backup from '../views/Backup.vue'
import Profile from '../views/Profile.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/auth', component: Auth },
        {
            path: '/',
            component: DashboardLayout,
            meta: { requiresAuth: true },
            children: [
                { path: '', redirect: '/dashboard' },
                { path: 'dashboard', component: DashboardHome },
                { path: 'inventory', component: Inventory },
                { path: 'add', component: AddProduct },
                { path: 'backup', component: Backup },
                { path: 'profile', component: Profile }
            ]
        }
    ]
})

router.beforeEach(async (to, from, next) => {
    const auth = useAuthStore()
    if (to.meta.requiresAuth) {
        const isValid = await auth.checkAuth()
        if (!isValid) {
            next('/auth')
        } else {
            next()
        }
    } else {
        next()
    }
})

export default router
