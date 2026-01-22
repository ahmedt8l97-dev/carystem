<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Save, ImagePlus, X } from 'lucide-vue-next'
import { compressImage } from '../lib/utils'


const router = useRouter()
const form = ref({
  product_number: '',
  product_name: '',
  car_name: '',
  type: '',
  quantity: 1,
  price_iqd: 0,
  wholesale_price_iqd: 0
})

const fileInput = ref(null)
const previewUrl = ref(null)
const loading = ref(false)

function onFileSelect(e) {
  const file = e.target.files[0]
  if (file) {
    previewUrl.value = URL.createObjectURL(file)
  }
}

function clearImage() {
  previewUrl.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const stripCommas = (str) => String(str).replace(/,/g, '');

function formatInputPrice(e, field) {
  let val = e.target.value.replace(/,/g, '');
  if (!isNaN(val) && val !== '') {
    form.value[field] = Number(val).toLocaleString();
  }
}

async function submit() {
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('product_number', form.value.product_number)
    formData.append('product_name', form.value.product_name)
    formData.append('car_name', form.value.car_name)
    formData.append('product_type', form.value.type || 'قطع غيار')
    formData.append('quantity', form.value.quantity)
    formData.append('price_iqd', stripCommas(form.value.price_iqd))
    formData.append('wholesale_price_iqd', stripCommas(form.value.wholesale_price_iqd))
    
    // Add image if selected
    const file = fileInput.value?.files[0]
    if (file) {
      const compressed = await compressImage(file)
      formData.append('image', compressed)
    }
    
    const res = await fetch('/api/products', {
      method: 'POST',
      body: formData
    })
    
    if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'فشل الحفظ')
    }

    router.push('/inventory')
  } catch (e) {
    alert('خطأ: ' + e.message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="add-product-page">
    <header class="title-box">
      <h1>إضافة قطعة جديدة</h1>
    </header>

    <div class="glass-form-card">
      <form @submit.prevent="submit" class="form-layout">
        <!-- Sidebar: Image Upload -->
        <aside class="image-upload-section">
          <div class="image-picker-box" @click="!previewUrl && fileInput.click()">
            <input type="file" ref="fileInput" accept="image/*" class="hidden" @change="onFileSelect">
            
            <div v-if="previewUrl" class="preview-container">
              <img :src="previewUrl" alt="Preview">
              <button type="button" class="clear-img" @click.stop="clearImage">
                <X :size="18" />
              </button>
            </div>
            
            <div v-else class="upload-placeholder">
              <ImagePlus :size="48" :stroke-width="1.5" />
              <span>إضافة صورة المنتج</span>
            </div>
          </div>
          <p class="image-hint">يفضل استخدام صور واضحة وبدقة عالية للمنتج.</p>
        </aside>

        <!-- Main Form Fields -->
        <div class="form-inputs-grid">
          <div class="input-field">
            <label>رقم المنتج (اختياري)</label>
            <input v-model="form.product_number" placeholder="سيتم التوليد تلقائياً إذا ترك فارغاً">
          </div>
          
          <div class="input-field">
            <label>اسم المنتج</label>
            <input v-model="form.product_name" required placeholder="مثلاً: محرك كورولا">
          </div>

          <div class="input-field">
            <label>السيارة</label>
            <input v-model="form.car_name" required placeholder="مثلاً: Toyota">
          </div>

          <div class="input-field">
            <label>النوع</label>
            <input v-model="form.type" placeholder="مثلاً: كهربائيات">
          </div>

          <div class="input-field">
            <label>الكمية المتوفرة</label>
            <input type="number" v-model="form.quantity" required min="0">
          </div>

          <div class="input-field">
            <label>سعر البيع (IQD)</label>
            <input type="text" v-model="form.price_iqd" @input="e => formatInputPrice(e, 'price_iqd')" required placeholder="السعر">
          </div>

          <div class="input-field span-2">
            <label>سعر الجملة (IQD)</label>
            <input type="text" v-model="form.wholesale_price_iqd" @input="e => formatInputPrice(e, 'wholesale_price_iqd')" required placeholder="سعر الجملة">
          </div>

          <button class="submit-btn-premium" :disabled="loading">
            <Save v-if="!loading" :size="20" />
            <span>{{ loading ? 'جاري المزامنة...' : 'حفظ المنتج في النظام' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.add-product-page { 
  max-width: 1000px; 
  margin: 0 auto; 
  padding: 40px 20px 100px;
}

.title-box {
  margin-bottom: 40px;
  text-align: center;
}

.title-box h1 {
  font-size: 32px;
  background: linear-gradient(135deg, #fff, var(--system-gray));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}

.glass-form-card {
  background: rgba(28, 28, 30, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 28px;
  padding: 40px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.3);
}

.form-layout { 
  display: grid; 
  grid-template-columns: 300px 1fr;
  gap: 40px; 
}

.image-upload-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.image-picker-box {
  aspect-ratio: 1/1;
  background: rgba(255,255,255,0.03);
  border: 2px dashed rgba(255,255,255,0.1);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s;
}

.image-picker-box:hover {
  background: rgba(255,255,255,0.05);
  border-color: var(--system-blue);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--system-gray);
}

.preview-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.preview-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.clear-img {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
}

.form-inputs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.span-2 { grid-column: span 2; }

.input-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-field label {
  font-size: 13px;
  font-weight: 600;
  color: var(--system-gray);
  padding-right: 4px;
}

.input-field input {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  padding: 14px 18px;
  border-radius: 14px;
  color: #fff;
  font-size: 15px;
  transition: all 0.2s;
}

.input-field input:focus {
  outline: none;
  border-color: var(--system-blue);
  background: rgba(10, 132, 255, 0.05);
  box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.1);
}

.submit-btn-premium {
  grid-column: span 2;
  height: 58px;
  background: var(--system-blue);
  color: white;
  border: none;
  border-radius: 18px;
  font-size: 17px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  margin-top: 10px;
  transition: all 0.3s;
  box-shadow: 0 8px 24px rgba(10, 132, 255, 0.3);
}

.submit-btn-premium:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(10, 132, 255, 0.4);
}

.submit-btn-premium:active:not(:disabled) {
  transform: scale(0.96);
  opacity: 0.8;
}

.submit-btn-premium:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.hidden { display: none; }

@media (max-width: 850px) {
  .form-layout { grid-template-columns: 1fr; }
  .image-upload-section { align-items: center; }
  .image-picker-box { width: 200px; }
  .form-inputs-grid { grid-template-columns: 1fr; }
  .span-2 { grid-column: auto; }
  .submit-btn-premium { grid-column: auto; }
  .glass-form-card { padding: 24px; }
}
</style>
