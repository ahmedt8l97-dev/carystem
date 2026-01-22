<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { convex } from '../lib/convex'
import { api } from '../../../convex/_generated/api'
import { User, Lock, UserPlus, Image as ImageIcon } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

const isLogin = ref(true)
const loading = ref(false)
const error = ref('')
const rememberMe = ref(false)

const loginData = ref({ username: '', password: '' })
const signupData = ref({ 
  name: '', 
  family_name: '', 
  username: '', 
  password: '',
  photo: null 
})
const fileInput = ref(null)

// Load saved credentials on mount
onMounted(() => {
  const savedCreds = localStorage.getItem('saved_login')
  if (savedCreds) {
    try {
      const parsed = JSON.parse(savedCreds)
      loginData.value.username = parsed.username
      loginData.value.password = parsed.password
      rememberMe.value = true
    } catch (e) {}
  }
})

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(loginData.value.username, loginData.value.password)
    
    // Save credentials if "Remember Me" is checked
    if (rememberMe.value) {
      localStorage.setItem('saved_login', JSON.stringify({
        username: loginData.value.username,
        password: loginData.value.password
      }))
    } else {
      localStorage.removeItem('saved_login')
    }
    
    router.push('/')
  } catch (e) {
    error.value = 'اسم المستخدم أو كلمة المرور غير صحيحة'
  } finally {
    loading.value = false
  }
}

async function handleSignup() {
  loading.value = true
  error.value = ''
  try {
    const msgBuffer = new TextEncoder().encode(signupData.value.password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const passwordHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    let photoUrl = undefined
    const file = fileInput.value?.files[0]
    if (file) {
       const postUrl = await convex.mutation(api.users.generateUploadUrl)
       const result = await fetch(postUrl, {
         method: "POST",
         headers: { "Content-Type": file.type },
         body: file,
       })
       const { storageId } = await result.json()
       photoUrl = storageId
    }

    const { password, photo, ...otherData } = signupData.value;
    await convex.mutation(api.users.createUser, {
      ...otherData,
      passwordHash,
      role: 'employee',
      photo: photoUrl
    })

    // Log in automatically after signup to get a valid FastAPI session token
    await auth.login(signupData.value.username, signupData.value.password)
    router.push('/')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <div class="app-logo">
          <User :size="40" color="var(--system-blue)" />
        </div>
        <h2>{{ isLogin ? 'تسجيل الدخول' : 'إنشاء حساب' }}</h2>
        <p>{{ isLogin ? 'أدخل بياناتك للمتابعة' : 'أدخل بياناتك للانضمام إلينا' }}</p>
      </div>

      <div v-if="error" class="error-pill">{{ error }}</div>

      <form v-if="isLogin" @submit.prevent="handleLogin" class="form-body">
        <div class="form-group">
          <label>اسم المستخدم</label>
          <div class="input-icon-wrapper">
             <User class="input-icon" :size="18" />
             <input v-model="loginData.username" type="text" placeholder="Username" required>
          </div>
        </div>
        <div class="form-group">
          <label>كلمة المرور</label>
          <div class="input-icon-wrapper">
             <Lock class="input-icon" :size="18" />
             <input v-model="loginData.password" type="password" placeholder="Password" required>
          </div>
         </div>
         <div class="remember-me-row">
           <label class="checkbox-label">
             <input type="checkbox" v-model="rememberMe">
             <span>تذكرني في المرة القادمة</span>
           </label>
         </div>
         <button class="btn-primary full-width" :disabled="loading">
           {{ loading ? 'جاري التحميل...' : 'دخول' }}
         </button>
      </form>

      <form v-else @submit.prevent="handleSignup" class="form-body">
        <div class="form-row">
           <div class="form-group">
             <label>الاسم</label>
             <input v-model="signupData.name" required>
           </div>
           <div class="form-group">
             <label>اللقب</label>
             <input v-model="signupData.family_name" required>
           </div>
        </div>
        <div class="form-group">
          <label>صورة الملف الشخصي</label>
          <div class="file-dummy" @click="fileInput.click()">
            <ImageIcon :size="20" />
            <span>{{ fileInput?.files?.[0]?.name || 'اختر صورة...' }}</span>
          </div>
          <input type="file" ref="fileInput" class="hidden" accept="image/*">
        </div>
        <div class="form-group">
          <label>اسم المستخدم</label>
          <input v-model="signupData.username" required>
        </div>
        <div class="form-group">
          <label>كلمة المرور</label>
          <input v-model="signupData.password" type="password" required>
        </div>
        <button class="btn-primary full-width" :disabled="loading">
          <UserPlus :size="18" />
          <span>{{ loading ? 'جاري المعالجة...' : 'إنشاء الحساب' }}</span>
        </button>
      </form>

      <div class="auth-footer">
        <button @click="isLogin = !isLogin" class="toggle-btn">
          {{ isLogin ? 'ليس لديك حساب؟ إنشاء حساب' : 'لديك حساب؟ تسجيل الدخول' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--system-bg);
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--system-secondary-bg);
  padding: 32px 24px;
}

.auth-header { text-align: center; margin-bottom: 32px; }
.app-logo { margin-bottom: 16px; }
.auth-header h2 { margin: 0; font-size: 24px; }
.auth-header p { color: var(--text-secondary); margin-top: 8px; font-size: 15px; }

.form-body { display: grid; gap: 16px; }

.input-icon-wrapper { position: relative; }
.input-icon { position: absolute; right: 12px; top: 12px; color: var(--system-gray-2); }
.input-icon-wrapper input { padding-right: 40px; }

.form-row { display: flex; gap: 12px; }
.form-row .form-group { flex: 1; }

.file-dummy {
  background: var(--system-tertiary-bg);
  padding: 12px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--system-gray);
  cursor: pointer;
}

.error-pill {
  background: rgba(255, 69, 58, 0.1);
  color: var(--system-red);
  padding: 10px;
  border-radius: 10px;
  text-align: center;
  margin-bottom: 20px;
  font-size: 14px;
}

.full-width { width: 100%; height: 50px; margin-top: 10px; }

.remember-me-row {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--system-blue);
}

.auth-footer { margin-top: 24px; text-align: center; }
.toggle-btn { background: none; border: none; color: var(--system-blue); font-size: 14px; cursor: pointer; }
.hidden { display: none; }
</style>
