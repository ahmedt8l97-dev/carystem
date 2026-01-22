<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { 
  Home, 
  Box, 
  Plus, 
  CloudDownload,
  LogOut,
  User
} from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/auth')
}
</script>

<template>
  <div class="dashboard-layout">
    <!-- Desktop Sidebar -->
    <aside class="sidebar desktop-only">
      <div class="sidebar-brand">
        <div class="logo-box">
          <span class="logo-icon">🚗</span>
        </div>
        <div class="logo-text-stack">
          <span class="logo-main">xCar</span>
          <span class="logo-sub">نظام إدارة المخزون</span>
        </div>
      </div>
      
      <nav class="side-nav">
        <router-link to="/dashboard" class="nav-link">
          <div class="nav-icon-box"><Home :size="20" /></div>
          <span>لوحة التحكم</span>
        </router-link>
        <router-link to="/inventory" class="nav-link">
          <div class="nav-icon-box"><Box :size="20" /></div>
          <span>المخزون العام</span>
        </router-link>
        <router-link to="/add" class="nav-link">
          <div class="nav-icon-box"><Plus :size="20" /></div>
          <span>إضافة منتج</span>
        </router-link>
        <router-link to="/profile" class="nav-link">
          <div class="nav-icon-box"><User :size="20" /></div>
          <span>إعدادات النظام</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-cell">
          <div class="user-avatar">{{ auth.user?.name?.[0] }}</div>
          <div class="user-details">
            <span class="u-name">{{ auth.user?.name }}</span>
            <span class="u-role">{{ auth.user?.role === 'admin' ? 'مدير' : 'موظف' }}</span>
          </div>
        </div>
        <button @click="logout" class="footer-logout">
          <LogOut :size="18" />
          <span>تسجيل الخروج</span>
        </button>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="page-fade">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
      <div class="mobile-spacer mobile-only"></div>
    </main>

    <!-- Mobile Tab Bar (iOS Style) -->
    <nav class="mobile-tab-bar mobile-only">
      <router-link to="/dashboard" class="tab-item">
        <Home :size="22" />
        <span>الرئيسية</span>
      </router-link>
      <router-link to="/inventory" class="tab-item">
        <Box :size="22" />
        <span>المخزون</span>
      </router-link>
      <router-link to="/add" class="tab-item">
        <Plus :size="22" />
        <span>إضافة</span>
      </router-link>
      <router-link to="/profile" class="tab-item">
        <User :size="22" />
        <span>حسابي</span>
      </router-link>
    </nav>
  </div>
</template>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background: var(--system-bg);
}

/* Sidebar Styling */
.sidebar {
  width: 280px;
  background: rgba(28, 28, 30, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  padding: 32px 16px;
  position: sticky;
  top: 0;
  height: 100vh;
  z-index: 100;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 48px;
  padding: 0 8px;
}

.logo-box {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--system-blue), #5ac8fa);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 8px 16px rgba(10, 132, 255, 0.3);
}

.logo-text-stack {
  display: flex;
  flex-direction: column;
}

.logo-main {
  font-size: 22px;
  font-weight: 900;
  color: #fff;
  letter-spacing: -0.5px;
  line-height: 1;
}

.logo-sub {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
  margin-top: 2px;
}

/* Nav links */
.side-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-icon-box {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.2s;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  transform: translateX(-4px);
}

.nav-link:active {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(0.98);
}

.nav-link.router-link-active {
  background: rgba(10, 132, 255, 0.1);
  color: var(--system-blue);
}

.nav-link.router-link-active .nav-icon-box {
  background: var(--system-blue);
  color: #fff;
  box-shadow: 0 4px 12px rgba(10, 132, 255, 0.3);
}

/* Sidebar Footer */
.sidebar-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
}

.user-avatar {
  width: 38px;
  height: 38px;
  background: var(--system-tertiary-bg);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: var(--system-blue);
}

.user-details {
  display: flex;
  flex-direction: column;
}

.u-name { font-size: 14px; font-weight: 700; color: #fff; }
.u-role { font-size: 11px; color: var(--text-secondary); }

.footer-logout {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(255, 69, 58, 0.1);
  border: none;
  border-radius: 12px;
  color: var(--system-red);
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.footer-logout:hover {
  background: var(--system-red);
  color: #fff;
}

/* Main Content Area */
.main-content {
  flex: 1;
  background: var(--system-bg);
  height: 100vh;
  overflow-y: auto;
}

.content-wrapper {
  min-height: 100%;
}

/* Transitions */
.content-wrapper {
  position: relative;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-fade-leave-active {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

.page-fade-enter-from {
  opacity: 0;
  transform: scale(0.98) translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: scale(1.02) translateY(-10px);
}

/* Mobile Tab Bar */
.mobile-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(28, 28, 30, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  justify-content: space-around;
  padding-bottom: env(safe-area-inset-bottom);
  border-top: 0.5px solid var(--border);
  z-index: 1000;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--system-gray);
  font-size: 10px;
  gap: 3px;
  flex: 1;
  text-decoration: none;
  transition: opacity 0.2s;
}

.tab-item:active {
  opacity: 0.6;
}

.tab-item.router-link-active {
  color: var(--system-blue);
}

.mobile-spacer { height: 84px; }

.desktop-only { display: flex; }
.mobile-only { display: none; }

@media (max-width: 768px) {
  .desktop-only { display: none; }
  .mobile-only { display: flex; }
  .main-content { padding: 0; } /* Padding handled by views */
}
</style>
