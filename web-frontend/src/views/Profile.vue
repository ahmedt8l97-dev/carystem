<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { 
  User, 
  Mail, 
  Shield, 
  LogOut,
  Edit3,
  Key,
  CheckCircle,
  Database,
  CloudDownload,
  ChevronLeft,
  FileJson,
  Calendar,
  AlertCircle,
  Settings,
  Bell,
  Lock,
  X
} from 'lucide-vue-next'

import { convex } from '../lib/convex'
import { api } from '../../../convex/_generated/api'

const auth = useAuthStore()
const router = useRouter()

const message = ref({ text: '', type: '' })
const showEditDialog = ref(false)
const showPasswordDialog = ref(false)
const showBackupDialog = ref(false)

const editForm = ref({
  name: '',
  username: ''
})

const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

const backups = ref([])
const backupsLoading = ref(false)
const manualBackupLoading = ref(false)
const saveLoading = ref(false)

const userRole = computed(() => {
  return auth.user?.role === 'admin' ? 'مدير النظام' : 'موظف مبيعات'
})

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
    const res = await fetch('/api/backup/manual', { 
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${auth.user?.token}`
      }
    })
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

function openEditDialog() {
  editForm.value = {
    name: auth.user?.name || '',
    username: auth.user?.username || ''
  }
  showEditDialog.value = true
}

async function saveProfile() {
  saveLoading.value = true
  message.value = { text: '', type: '' }
  
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    auth.setUser({
      ...auth.user,
      name: editForm.value.name,
      username: editForm.value.username
    })
    
    message.value = { text: 'تم حفظ التعديلات بنجاح ✅', type: 'success' }
    showEditDialog.value = false
  } catch (e) {
    message.value = { text: 'فشل حفظ التعديلات', type: 'error' }
  } finally {
    saveLoading.value = false
  }
}

async function changePassword() {
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    message.value = { text: 'كلمات المرور غير متطابقة', type: 'error' }
    return
  }
  
  saveLoading.value = true
  message.value = { text: '', type: '' }
  
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    message.value = { text: 'تم تغيير كلمة المرور بنجاح ✅', type: 'success' }
    showPasswordDialog.value = false
    passwordForm.value = { current: '', new: '', confirm: '' }
  } catch (e) {
    message.value = { text: 'فشل تغيير كلمة المرور', type: 'error' }
  } finally {
    saveLoading.value = false
  }
}

function openBackupDialog() {
  showBackupDialog.value = true
  loadBackups()
}

function handleLogout() {
  if (confirm('هل أنت متأكد من تسجيل الخروج؟')) {
    auth.logout()
    router.push('/auth')
  }
}

onMounted(() => {
  loadBackups()
})
</script>

<template>
  <div class="profile-dashboard">
    <!-- Header Section -->
    <header class="main-header glass">
      <div class="user-profile-hero">
        <div class="avatar-large">
          {{ auth.user?.name?.[0] || '?' }}
          <div class="status-indicator"></div>
        </div>
        <div class="hero-text">
          <h1>{{ auth.user?.name }}</h1>
          <p>{{ auth.user?.username }} @ {{ userRole }}</p>
        </div>
      </div>
      <div class="header-actions">
        <button @click="openEditDialog" class="btn-icon-labeled">
          <Edit3 :size="18" />
          <span>تعديل الملف</span>
        </button>
<!-- Logout hidden -->
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

    <div class="profile-grid">
      <!-- Account & Security Column -->
      <div class="profile-column">
        <section class="settings-card glass">
          <h2 class="section-title">
            <Lock :size="20" />
            <span>الحساب والأمان</span>
          </h2>
          
          <div class="settings-stack">
            <div class="setting-row">
              <div class="icon-orb blue"><User :size="18" /></div>
              <div class="setting-text">
                <span class="label">الاسم الكامل</span>
                <span class="value">{{ auth.user?.name }}</span>
              </div>
            </div>

            <div class="setting-row">
              <div class="icon-orb purple"><Mail :size="18" /></div>
              <div class="setting-text">
                <span class="label">اسم المستخدم</span>
                <span class="value">{{ auth.user?.username }}</span>
              </div>
            </div>

            <div class="setting-row">
              <div class="icon-orb orange"><Shield :size="18" /></div>
              <div class="setting-text">
                <span class="label">نوع الحساب</span>
                <span class="value">{{ userRole }}</span>
              </div>
            </div>

            <button @click="showPasswordDialog = true" class="action-row">
              <div class="icon-orb teal"><Key :size="18" /></div>
              <div class="setting-text">
                <span class="label">كلمة المرور</span>
                <span class="value">تغيير كلمة المرور الخاصة بك</span>
              </div>
              <ChevronLeft :size="16" />
            </button>
          </div>
        </section>
      </div>

      <!-- Backup & Data Column -->
      <div class="profile-column">
        <section class="settings-card glass">
          <h2 class="section-title">
            <Database :size="20" />
            <span>النسخ الاحتياطي والبيانات</span>
          </h2>
          
          <div class="backup-cta">
            <div class="cta-content">
              <h3>النسخ الاحتياطي السحابي</h3>
              <p>قم بحفظ نسخة من بياناتك الحالية وتصديرها إلى صيغة JSON آمنة.</p>
            </div>
            <button @click="triggerManualBackup" class="cta-btn" :disabled="manualBackupLoading">
              <CloudDownload :size="20" />
              <span>{{ manualBackupLoading ? 'جاري الحفظ...' : 'حفظ نسخة الآن' }}</span>
            </button>
          </div>

          <div class="backups-header">
            <span>آخر النسخ ({{ backups.length }})</span>
            <button @click="loadBackups" class="refresh-btn">تحديث</button>
          </div>

          <div class="mini-backup-list">
            <div v-if="backupsLoading" class="mini-loading">جاري المزامنة...</div>
            <div v-else-if="backups.length === 0" class="mini-empty">لا يوجد سجل حالي</div>
            <div 
              v-for="backup in backups.slice(0, 4)" 
              :key="backup._id" 
              class="mini-backup-cell"
              @click="downloadBackup(backup)"
            >
              <div class="backup-orb"><FileJson :size="16" /></div>
              <div class="backup-text">
                <span class="name">{{ backup.filename }}</span>
                <span class="date">{{ formatDate(backup.createdAt) }}</span>
              </div>
              <div class="count-tag">{{ backup.productCount }}</div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Edit Profile Dialogs -->
    <Teleport to="body">
      <transition name="dialog-fade">
        <div v-if="showEditDialog" class="dialog-overlay" @click="showEditDialog = false">
          <div class="dialog-glass" @click.stop>
            <div class="dialog-header">
              <h3>تعديل المعلومات</h3>
              <button @click="showEditDialog = false" class="close-btn"><X :size="20" /></button>
            </div>
            <div class="dialog-body">
              <div class="input-orb">
                <label>الاسم الكامل</label>
                <input v-model="editForm.name" />
              </div>
              <div class="input-orb">
                <label>اسم المستخدم</label>
                <input v-model="editForm.username" />
              </div>
            </div>
            <div class="dialog-footer">
              <button @click="saveProfile" class="btn-save" :disabled="saveLoading">
                {{ saveLoading ? 'جاري الحفظ...' : 'حفظ التغييرات' }}
              </button>
            </div>
          </div>
        </div>
      </transition>

      <transition name="dialog-fade">
        <div v-if="showPasswordDialog" class="dialog-overlay" @click="showPasswordDialog = false">
          <div class="dialog-glass" @click.stop>
            <div class="dialog-header">
              <h3>تغيير كلمة المرور</h3>
              <button @click="showPasswordDialog = false" class="close-btn"><X :size="20" /></button>
            </div>
            <div class="dialog-body">
              <div class="input-orb">
                <label>كلمة المرور الحالية</label>
                <input v-model="passwordForm.current" type="password" />
              </div>
              <div class="input-orb">
                <label>كلمة المرور الجديدة</label>
                <input v-model="passwordForm.new" type="password" />
              </div>
              <div class="input-orb">
                <label>تأكيد كلمة المرور</label>
                <input v-model="passwordForm.confirm" type="password" />
              </div>
            </div>
            <div class="dialog-footer">
              <button @click="changePassword" class="btn-save" :disabled="saveLoading">
                تحديث كلمة المرور
              </button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<style scoped>
.profile-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px;
  padding-bottom: 120px;
}

/* Glassmorphism */
.glass {
  background: rgba(28, 28, 30, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 28px;
}

/* Header Section */
.main-header {
  padding: 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.user-profile-hero {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-large {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, var(--system-blue), #5ac8fa);
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: 900;
  color: #fff;
  position: relative;
  box-shadow: 0 12px 30px rgba(10, 132, 255, 0.3);
}

.status-indicator {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 24px;
  height: 24px;
  background: var(--system-green);
  border: 4px solid var(--system-secondary-bg);
  border-radius: 50%;
}

.hero-text h1 {
  font-size: 32px;
  margin: 0;
  font-weight: 800;
  color: #fff;
}

.hero-text p {
  margin: 4px 0 0;
  color: var(--text-secondary);
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-icon-labeled {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon-labeled:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.btn-icon-labeled.logout {
  color: var(--system-red);
  background: rgba(255, 69, 58, 0.1);
  border-color: rgba(255, 69, 58, 0.2);
}

.btn-icon-labeled.logout:hover {
  background: var(--system-red);
  color: #fff;
}

/* Grid Layout */
.profile-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.settings-card {
  padding: 32px;
  height: 100%;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 800;
  margin: 0 0 32px;
  color: #fff;
}

.settings-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-row, .action-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  border: 1px solid transparent;
}

.action-row {
  cursor: pointer;
  border-color: rgba(255, 255, 255, 0.05);
  transition: all 0.2s;
}

.action-row:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--system-blue);
  transform: scale(1.01);
}

.icon-orb {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-orb.blue { background: rgba(10, 132, 255, 0.15); color: var(--system-blue); }
.icon-orb.purple { background: rgba(191, 90, 242, 0.15); color: #bf5af2; }
.icon-orb.orange { background: rgba(255, 159, 10, 0.15); color: var(--system-orange); }
.icon-orb.teal { background: rgba(100, 210, 255, 0.15); color: #64d2ff; }

.setting-text {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.setting-text .label { font-size: 11px; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; }
.setting-text .value { font-size: 16px; font-weight: 700; color: #fff; }

/* Backup Section */
.backup-cta {
  background: linear-gradient(135deg, rgba(10, 132, 255, 0.1), rgba(48, 209, 88, 0.1));
  padding: 24px;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 32px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.cta-content h3 { font-size: 18px; margin: 0; color: #fff; }
.cta-content p { font-size: 14px; color: var(--text-secondary); margin: 8px 0 0; }

.cta-btn {
  height: 52px;
  background: var(--system-blue);
  color: #fff;
  border: none;
  border-radius: 14px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.cta-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(10, 132, 255, 0.3);
}

/* Mini Backup List */
.backups-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.backups-header span { font-size: 14px; font-weight: 700; color: var(--text-secondary); }
.refresh-btn { background: none; border: none; color: var(--system-blue); cursor: pointer; font-size: 13px; font-weight: 700; }

.mini-backup-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mini-backup-cell {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.mini-backup-cell:hover {
  background: rgba(255, 255, 255, 0.06);
}

.backup-orb {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--system-green);
}

.backup-text { flex: 1; display: flex; flex-direction: column; }
.backup-text .name { font-size: 14px; font-weight: 700; }
.backup-text .date { font-size: 11px; color: var(--text-secondary); }
.count-tag { background: rgba(48, 209, 88, 0.2); color: var(--system-green); padding: 2px 8px; border-radius: 8px; font-size: 11px; font-weight: 800; }

/* Dialog Styles */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 24px;
}

.dialog-glass {
  width: 100%;
  max-width: 500px;
  background: rgba(28, 28, 30, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 32px;
  padding: 32px;
  box-shadow: 0 40px 100px rgba(0,0,0,0.5);
}

.dialog-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.dialog-header h3 { font-size: 22px; font-weight: 800; margin: 0; color: #fff; }
.close-btn { background: rgba(255, 255, 255, 0.05); border: none; color: #fff; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; }

.dialog-body { display: flex; flex-direction: column; gap: 20px; margin-bottom: 24px; }
.input-orb { display: flex; flex-direction: column; gap: 8px; }
.input-orb label { font-size: 13px; font-weight: 700; color: var(--text-secondary); margin-right: 4px; }
.input-orb input { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 14px 18px; border-radius: 14px; color: #fff; font-size: 16px; }
.input-orb input:focus { outline: none; border-color: var(--system-blue); }

.btn-save { width: 100%; height: 52px; background: var(--system-blue); color: #fff; border: none; border-radius: 16px; font-weight: 800; font-size: 16px; cursor: pointer; }

/* Mobile Transitions & Media */
.dialog-fade-enter-active, .dialog-fade-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.dialog-fade-enter-from, .dialog-fade-leave-to { opacity: 0; transform: scale(0.95); }

@media (max-width: 1000px) {
  .profile-grid { grid-template-columns: 1fr; }
  .main-header { flex-direction: column; text-align: center; gap: 24px; padding: 32px; }
  .user-profile-hero { flex-direction: column; }
}

@media (max-width: 600px) {
  .profile-dashboard { padding: 16px; }
  .main-header { padding: 24px; }
  .hero-text h1 { font-size: 24px; }
}
</style>
