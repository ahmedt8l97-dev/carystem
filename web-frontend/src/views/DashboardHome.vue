<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { 
  TrendingUp, 
  Package, 
  AlertTriangle,
  ShoppingBag,
  Database,
  ChevronLeft,
  Bell,
  LayoutDashboard,
  CloudDownload,
  FileJson,
  Calendar,
  Settings,
  User,
  Key,
  Shield,
  CheckCircle,
  AlertCircle,
  Plus,
  Box
} from 'lucide-vue-next'

import { convex } from '../lib/convex'
import { api } from '../../../convex/_generated/api'

const auth = useAuthStore()
const stats = ref(null)
const loading = ref(true)
const backups = ref([])
const backupsLoading = ref(false)
const manualBackupLoading = ref(false)
const message = ref({ text: '', type: '' })

async function loadStats() {
  loading.value = true
  try {
    const res = await fetch('/api/stats')
    if (res.ok) {
      stats.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to load stats:', e)
  } finally {
    loading.value = false
  }
}

async function loadBackups() {
  backupsLoading.value = true
  try {
    const data = await convex.query(api.backups.getBackups)
    backups.value = data
  } catch (e) {
    console.error(e)
  } finally {
    backupsLoading.value = false
  }
}

async function triggerManualBackup() {
  manualBackupLoading.value = true
  message.value = { text: '', type: '' }
  try {
    const res = await fetch('/api/backup/manual', { method: 'POST' })
    const data = await res.json()
    
    if (res.ok) {
      message.value = { text: 'تم إنشاء النسخة الاحتياطية بنجاح ✅', type: 'success' }
      await loadBackups()
    } else {
      throw new Error(data.detail || 'فشل الحفظ')
    }
  } catch (e) {
    message.value = { text: 'خطأ: ' + e.message, type: 'error' }
  } finally {
    manualBackupLoading.value = false
  }
}

function downloadBackup(backup) {
  const blob = new Blob([backup.data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = backup.filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('ar-IQ', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getProgressWidth(count) {
  if (!stats.value?.overview?.total_products) return '0%'
  return (count / stats.value.overview.total_products * 100) + '%'
}

onMounted(() => {
  loadStats()
  loadBackups()
})
</script>

<template>
  <div class="dashboard-unified">
    <!-- Header -->
    <header class="main-header">
      <div class="header-content">
        <div class="icon-box">
          <LayoutDashboard :size="32" class="header-icon" />
        </div>
        <div class="title-stack">
          <h1>لوحة تحكم xCar</h1>
          <p>أهلاً بك مجدداً، {{ auth.user?.name }}</p>
        </div>
      </div>
      <div class="header-actions">
        <div class="live-status">
          <span class="pulse-dot"></span>
          <span>النظام نشط</span>
        </div>
        <div class="user-badge-desktop">
          <div class="avatar">{{ auth.user?.name?.[0] }}</div>
          <div class="user-info">
            <span class="user-name">{{ auth.user?.name }}</span>
            <span class="user-role">{{ auth.user?.role === 'admin' ? 'مدير النظام' : 'موظف' }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Alert Messages -->
    <transition name="fade">
      <div v-if="message.text" :class="['alert-banner', message.type]">
        <CheckCircle v-if="message.type === 'success'" :size="18" />
        <AlertCircle v-else :size="18" />
        <span>{{ message.text }}</span>
      </div>
    </transition>

    <div v-if="loading" class="loading-container">
       <div class="loader-spinner"></div>
       <span>جاري مزامنة البيانات...</span>
    </div>
    
    <div v-else class="unified-grid">
      <!-- Top Row: Stats (Full Width) -->
      <section class="grid-span-full">
        <div class="stats-grid">
          <div class="stat-card blue glass">
            <div class="stat-icon"><Package :size="28" /></div>
            <div class="stat-info">
              <span class="stat-label">أنواع القطع</span>
              <span class="stat-value">{{ stats?.overview?.total_products || 0 }}</span>
            </div>
          </div>

          <div class="stat-card green glass">
            <div class="stat-icon"><TrendingUp :size="28" /></div>
            <div class="stat-info">
              <span class="stat-label">القيمة الإجمالية</span>
              <span class="stat-value">{{ (stats?.overview?.total_value || 0).toLocaleString() }} <small>IQD</small></span>
            </div>
          </div>

          <div class="stat-card orange glass">
            <div class="stat-icon"><AlertTriangle :size="28" /></div>
            <div class="stat-info">
              <span class="stat-label">أصناف منتهية</span>
              <span class="stat-value">{{ stats?.overview?.out_of_stock || 0 }}</span>
            </div>
          </div>

          <div class="stat-card purple glass">
            <div class="stat-icon"><ShoppingBag :size="28" /></div>
            <div class="stat-info">
              <span class="stat-label">إجمالي الكمية</span>
              <span class="stat-value">{{ stats?.overview?.total_items || 0 }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Main Column: Actions and Distribution -->
      <div class="main-column">
        <!-- Quick Actions -->
        <section class="content-section glass">
          <h2 class="section-title">
            <Settings :size="20" />
            <span>الوصول السريع</span>
          </h2>
          <div class="actions-grid-desktop">
            <router-link to="/add" class="desktop-action-card blue">
              <div class="action-icon"><Plus :size="24" /></div>
              <div class="action-content">
                <h3>إضافة منتج</h3>
                <p>تسجيل صنف جديد في النظام</p>
              </div>
            </router-link>

            <router-link to="/inventory" class="desktop-action-card green">
              <div class="action-icon"><Box :size="24" /></div>
              <div class="action-content">
                <h3>المستودع</h3>
                <p>إدارة وتعديل المخزون الحالي</p>
              </div>
            </router-link>

            <router-link to="/profile" class="desktop-action-card purple">
              <div class="action-icon"><User :size="24" /></div>
              <div class="action-content">
                <h3>الإعدادات</h3>
                <p>تخصيص ملفك الشخصي</p>
              </div>
            </router-link>
          </div>
        </section>

        <!-- Distribution -->
        <section class="content-section glass">
          <h2 class="section-title">
            <Database :size="20" />
            <span>توزيع المخزون حسب النوع</span>
          </h2>
          <div class="car-distribution-grid">
            <div v-for="(data, name) in stats?.by_car" :key="name" class="dist-card">
              <div class="dist-header">
                <span class="car-name">{{ name }}</span>
                <span class="car-count">{{ data.count }} قطعة</span>
              </div>
              <div class="progress-bar-container">
                <div 
                  class="progress-fill" 
                  :style="{ 
                    width: getProgressWidth(data.count),
                    boxShadow: '0 0 10px rgba(10, 132, 255, 0.3)'
                  }"
                ></div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Side Column: Alerts and Backups -->
      <div class="side-column">
        <!-- Alerts -->
        <section class="content-section glass alerts-section">
          <h2 class="section-title">
            <Bell :size="20" />
            <span>تنبيهات النظام</span>
          </h2>
          
          <div v-if="stats?.low_stock.length > 0" class="mini-alerts-list">
            <div v-for="item in stats.low_stock" :key="item.product_number" class="mini-alert-item">
              <div class="alert-indicator"></div>
              <div class="alert-content">
                <span class="name">{{ item.product_name }}</span>
                <span class="meta">بقي {{ item.quantity }} قطع فقط</span>
              </div>
            </div>
          </div>
          <div v-else class="no-alerts-desktop">
            <CheckCircle :size="32" class="success-icon" />
            <p>جميع الأصناف متوفرة بكثرة</p>
          </div>
        </section>

        <!-- Backup -->
        <section class="content-section glass backup-section">
          <h2 class="section-title">
            <CloudDownload :size="20" />
            <span>النسخ الاحتياطي</span>
          </h2>
          
          <button 
            @click="triggerManualBackup" 
            class="backup-action-btn"
            :disabled="manualBackupLoading"
          >
            <Database :size="18" />
            <span>{{ manualBackupLoading ? 'جاري الحفظ...' : 'حفظ نسخة الآن' }}</span>
          </button>

          <div class="recent-backups">
            <div v-if="backupsLoading" class="mini-loading">جاري المزامنة...</div>
            <div v-else class="backup-mini-list">
              <div 
                v-for="backup in backups.slice(0, 3)" 
                :key="backup._id" 
                class="mini-backup-item"
                @click="downloadBackup(backup)"
              >
                <FileJson :size="16" />
                <div class="backup-name-container">
                  <span class="name">{{ backup.filename }}</span>
                  <span class="date">{{ formatDate(backup.createdAt) }}</span>
                </div>
                <ChevronLeft :size="14" />
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-unified { 
  max-width: 1440px;
  margin: 0 auto;
  padding: 20px 40px 100px;
}

/* Glassmorphism Classes */
.glass {
  background: rgba(28, 28, 30, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
}

/* Header Enhancements */
.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 20px 0;
}

.icon-box {
  width: 56px;
  height: 56px;
  background: rgba(10, 132, 255, 0.1);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(10, 132, 255, 0.2);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-stack h1 {
  font-size: 32px;
  margin: 0;
  font-weight: 800;
  background: linear-gradient(135deg, #fff, #8e8e93);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.title-stack p {
  margin: 4px 0 0;
  color: var(--text-secondary);
  font-size: 15px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 24px;
}

.live-status {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(48, 209, 88, 0.1);
  padding: 6px 14px;
  border-radius: 20px;
  color: var(--system-green);
  font-size: 13px;
  font-weight: 600;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: var(--system-green);
  border-radius: 50%;
  box-shadow: 0 0 10px var(--system-green);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.5; }
  100% { transform: scale(0.95); opacity: 1; }
}

.user-badge-desktop {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 18px 6px 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 100px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.avatar {
  width: 40px;
  height: 40px;
  background: var(--system-blue);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  box-shadow: 0 4px 12px rgba(10, 132, 255, 0.3);
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name { font-size: 14px; font-weight: 700; color: #fff; }
.user-role { font-size: 11px; color: var(--text-secondary); }

/* Unified Grid Layout */
.unified-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
}

.grid-span-full {
  grid-column: 1 / -1;
  margin-bottom: 8px;
}

/* Stats Cards Styling */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.3s ease, border-color 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  border-color: rgba(255, 255, 255, 0.2);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.blue .stat-icon { background: rgba(10, 132, 255, 0.15); color: var(--system-blue); }
.green .stat-icon { background: rgba(48, 209, 88, 0.15); color: var(--system-green); }
.orange .stat-icon { background: rgba(255, 159, 10, 0.15); color: var(--system-orange); }
.purple .stat-icon { background: rgba(191, 90, 242, 0.15); color: #bf5af2; }

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
  margin-top: 4px;
}

/* Content Sections */
.main-column, .side-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.content-section {
  padding: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 24px;
  color: #fff;
}

.section-title span { flex: 1; }

/* Desktop Action Cards */
.actions-grid-desktop {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.desktop-action-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  text-decoration: none;
  transition: all 0.3s;
}

.desktop-action-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
}

.desktop-action-card:active {
  transform: scale(0.98);
  background: rgba(255, 255, 255, 0.12);
}

.desktop-action-card.blue:hover { border-color: var(--system-blue); }
.desktop-action-card.green:hover { border-color: var(--system-green); }
.desktop-action-card.purple:hover { border-color: #bf5af2; }

.action-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.blue .action-icon { background: var(--system-blue); color: #fff; }
.green .action-icon { background: var(--system-green); color: #fff; }
.purple .action-icon { background: #bf5af2; color: #fff; }

.action-content h3 { font-size: 16px; margin: 0; color: #fff; }
.action-content p { font-size: 12px; margin: 4px 0 0; color: var(--text-secondary); }

/* Distribution Cards */
.car-distribution-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.dist-card {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
}

.dist-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.car-name { font-weight: 600; font-size: 14px; }
.car-count { color: var(--system-blue); font-weight: 800; font-size: 14px; }

.progress-bar-container {
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--system-blue), var(--system-green));
  border-radius: 3px;
}

/* Alerts and Backup Area */
.mini-alerts-list { display: grid; gap: 12px; }
.mini-alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 69, 58, 0.05);
  border-radius: 14px;
  border: 1px solid rgba(255, 69, 58, 0.1);
}

.alert-indicator {
  width: 8px;
  height: 8px;
  background: var(--system-red);
  border-radius: 50%;
}

.alert-content { display: flex; flex-direction: column; }
.alert-content .name { font-size: 13px; font-weight: 700; color: #fff; }
.alert-content .meta { font-size: 11px; color: var(--system-red); opacity: 0.8; }

.no-alerts-desktop {
  text-align: center;
  padding: 30px 10px;
}

.success-icon { color: var(--system-green); margin-bottom: 12px; }

.backup-action-btn {
  width: 100%;
  height: 48px;
  background: var(--system-blue);
  border: none;
  border-radius: 14px;
  color: #fff;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: all 0.2s;
}

.backup-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(10, 132, 255, 0.3);
}

.backup-action-btn:active {
  transform: scale(0.96);
  opacity: 0.9;
}

.backup-mini-list { display: grid; gap: 8px; }
.mini-backup-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.mini-backup-item:hover { background: rgba(255, 255, 255, 0.08); }
.mini-backup-item:active { background: rgba(255, 255, 255, 0.15); transform: scale(0.98); }
.backup-name-container { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.backup-name-container .name { font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.backup-name-container .date { font-size: 10px; color: var(--text-secondary); }

/* Mobile Adaptations */
@media (max-width: 1100px) {
  .unified-grid {
    grid-template-columns: 1fr;
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-unified { padding: 16px 16px 120px; }
  .main-header { flex-direction: column; align-items: flex-start; gap: 20px; }
  .header-actions { width: 100%; justify-content: space-between; }
  .stats-grid { grid-template-columns: 1fr; }
  .actions-grid-desktop { grid-template-columns: 1fr; }
  .car-distribution-grid { grid-template-columns: 1fr; }
  .title-stack h1 { font-size: 24px; }
}

/* Loading Animation */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100px 0;
  gap: 20px;
  color: var(--text-secondary);
}

.loader-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(10, 132, 255, 0.1);
  border-top-color: var(--system-blue);
  border-radius: 50%;
  animation: spin 1s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Alert Banner Fade */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
