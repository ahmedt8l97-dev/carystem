<script setup>
import { ref, onMounted } from 'vue'
import { 
  CloudDownload, 
  History, 
  CheckCircle2, 
  AlertCircle,
  FileJson,
  Calendar,
  Database
} from 'lucide-vue-next'

import { convex } from '../lib/convex'
import { api } from '../../../convex/_generated/api'

const backups = ref([])
const loading = ref(false)
const manualLoading = ref(false)
const message = ref({ text: '', type: '' })

async function loadBackups() {
  loading.value = true
  try {
    const data = await convex.query(api.backups.getBackups)
    backups.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function triggerManualBackup() {
  manualLoading.value = true
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
    manualLoading.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('ar-IQ', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
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

onMounted(loadBackups)
</script>

<template>
  <div class="backup-page-mobile">
    <header class="mobile-header">
      <h1>النسخ الاحتياطي</h1>
      <p>احمِ بياناتك بضغطة واحدة</p>
    </header>

    <div class="mobile-content">
      <!-- Main Action Card -->
      <div class="action-card-mobile card">
        <div class="icon-badge">
          <Database :size="28" />
        </div>
        
        <div class="action-text">
          <h3>إنشاء نسخة احتياطية</h3>
          <p>حفظ كامل لبيانات المخزون وإرسالها للتليجرام</p>
        </div>

        <button 
          @click="triggerManualBackup" 
          class="btn-backup-mobile"
          :disabled="manualLoading"
        >
          <CloudDownload :size="20" />
          <span>{{ manualLoading ? 'جاري الحفظ...' : 'نسخ الآن' }}</span>
        </button>

        <div v-if="message.text" :class="['alert-mobile', message.type]">
          <CheckCircle2 v-if="message.type === 'success'" :size="14" />
          <AlertCircle v-else :size="14" />
          <span>{{ message.text }}</span>
        </div>
      </div>

      <!-- History Section -->
      <div class="history-section-mobile">
        <div class="section-header-mobile">
          <History :size="18" />
          <h3>السجل</h3>
          <span class="count-badge" v-if="backups.length">{{ backups.length }}</span>
        </div>

        <div v-if="loading" class="loading-mobile">جاري التحميل...</div>

        <div v-else-if="backups.length === 0" class="empty-mobile">
          <FileJson :size="48" :stroke-width="1" />
          <p>لا توجد نسخ احتياطية بعد</p>
        </div>

        <div v-else class="backup-list-mobile">
          <div 
            v-for="backup in backups" 
            :key="backup._id" 
            class="backup-item-mobile"
            @click="downloadBackup(backup)"
          >
            <div class="item-icon">
              <FileJson :size="20" />
            </div>
            <div class="item-info">
              <span class="item-name">{{ backup.filename }}</span>
              <span class="item-date">
                <Calendar :size="12" />
                {{ formatDate(backup.createdAt) }}
              </span>
            </div>
            <div class="item-badge">{{ backup.productCount }} قطعة</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.backup-page-mobile {
  padding-bottom: 100px;
  min-height: 100vh;
}

.mobile-header {
  padding: 24px 20px;
  text-align: center;
  background: linear-gradient(135deg, rgba(10, 132, 255, 0.1), rgba(48, 209, 88, 0.05));
  border-bottom: 1px solid var(--border);
}

.mobile-header h1 {
  font-size: 24px;
  font-weight: 800;
  margin: 0 0 8px;
}

.mobile-header p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.mobile-content {
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Action Card */
.action-card-mobile {
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-radius: 20px;
  background: var(--system-secondary-bg);
  border: 1px solid var(--border);
}

.icon-badge {
  width: 56px;
  height: 56px;
  background: rgba(10, 132, 255, 0.1);
  color: var(--system-blue);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.action-text {
  text-align: center;
}

.action-text h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px;
}

.action-text p {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.btn-backup-mobile {
  width: 100%;
  height: 54px;
  background: var(--system-blue);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-backup-mobile:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.btn-backup-mobile:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.alert-mobile {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.alert-mobile.success {
  background: rgba(48, 209, 88, 0.1);
  color: var(--system-green);
  border: 1px solid rgba(48, 209, 88, 0.2);
}

.alert-mobile.error {
  background: rgba(255, 69, 58, 0.1);
  color: var(--system-red);
  border: 1px solid rgba(255, 69, 58, 0.2);
}

/* History Section */
.history-section-mobile {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header-mobile {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
}

.section-header-mobile h3 {
  font-size: 17px;
  font-weight: 700;
  margin: 0;
  flex: 1;
}

.count-badge {
  background: var(--system-tertiary-bg);
  color: var(--system-blue);
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 12px;
}

.loading-mobile,
.empty-mobile {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-mobile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-mobile p {
  margin: 0;
  font-size: 14px;
}

/* Backup List */
.backup-list-mobile {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.backup-item-mobile {
  background: var(--system-secondary-bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.backup-item-mobile:active {
  transform: scale(0.98);
  background: var(--system-tertiary-bg);
}

.item-icon {
  width: 44px;
  height: 44px;
  background: rgba(48, 209, 88, 0.1);
  color: var(--system-green);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.item-name {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-date {
  font-size: 11px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.item-badge {
  background: var(--system-tertiary-bg);
  color: var(--system-orange);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 10px;
  white-space: nowrap;
}

/* Desktop Override */
@media (min-width: 768px) {
  .backup-page-mobile {
    max-width: 600px;
    margin: 0 auto;
  }
}
</style>
