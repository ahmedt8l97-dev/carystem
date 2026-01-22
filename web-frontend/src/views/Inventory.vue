<script setup>
import { ref, onMounted } from 'vue'
import { convex } from '../lib/convex'
import { api } from '../../../convex/_generated/api'
import { 
  RefreshCw, 
  Trash2, 
  ImageIcon,
  X
} from 'lucide-vue-next'
import { compressImage } from '../lib/utils'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()


const products = ref([])
const loading = ref(true)
const searchQuery = ref('')
const editingId = ref(null)
const editLoading = ref(false)
const editImageFile = ref(null)
const editForm = ref({
  product_number: '',
  product_name: '',
  car_name: '',
  model_number: '',
  type: '',
  quantity: 0,
  price_iqd: 0,
  wholesale_price_iqd: 0
})

const showImageModal = ref(false)
const selectedImage = ref('')

function openImage(url) {
  if (!url) return
  selectedImage.value = url
  showImageModal.value = true
}

function closeImage() {
  showImageModal.value = false
  selectedImage.value = ''
}

async function load() {
  loading.value = true
  try {
    products.value = await convex.query(api.products.getProducts, { 
      search: searchQuery.value || undefined 
    })
  } finally {
    loading.value = false
  }
}

let searchTimeout = null
function handleSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    load()
  }, 500)
}

function startEditing(p) {
  editingId.value = p._id
  editImageFile.value = null
  editForm.value = {
    product_number: p.product_number,
    product_name: p.product_name,
    car_name: p.car_name,
    model_number: p.model_number || '',
    type: p.type || '',
    quantity: p.quantity,
    price_iqd: p.price_iqd.toLocaleString(),
    wholesale_price_iqd: p.wholesale_price_iqd.toLocaleString()
  }
}

function formatInputPrice(e, field) {
  let val = e.target.value.replace(/,/g, '');
  if (!isNaN(val) && val !== '') {
    editForm.value[field] = Number(val).toLocaleString();
  }
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit() {
  editLoading.value = true
  const p = products.value.find(item => item._id === editingId.value)
  try {
    const formData = new FormData()
    const stripCommas = (str) => String(str).replace(/,/g, '');
    formData.append('product_number', editForm.value.product_number)
    formData.append('product_name', editForm.value.product_name)
    formData.append('car_name', editForm.value.car_name)
    formData.append('model_number', editForm.value.model_number)
    formData.append('product_type', editForm.value.type)
    formData.append('quantity', editForm.value.quantity)
    formData.append('price_iqd', stripCommas(editForm.value.price_iqd))
    formData.append('wholesale_price_iqd', stripCommas(editForm.value.wholesale_price_iqd))
    
    // Add image if selected
    if (editImageFile.value) {
      const compressed = await compressImage(editImageFile.value)
      formData.append('image', compressed)
    }

    const res = await fetch(`/api/products/${encodeURIComponent(p.product_number)}`, {
      method: 'PATCH',
      body: formData,
      headers: {
        'Authorization': `Bearer ${auth.user?.token}`
      }
    })
    
    if (!res.ok) throw new Error('فشل التحديث')
    
    await load()
    editingId.value = null
  } catch (e) {
    alert(e.message)
  } finally {
    editLoading.value = false
  }
}

const statusLoading = ref({})

async function updateStatus(productNumber, action) {
  const loadingKey = `${productNumber}-${action}`
  if (statusLoading.value[loadingKey]) return
  
  statusLoading.value[loadingKey] = true
  try {
    const res = await fetch(`/api/update-status/${encodeURIComponent(productNumber)}?action=${action}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${auth.user?.token}`
      }
    })
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Update failed');
    }
    
    await load()
  } catch (e) {
    alert('حدث خطأ: ' + e.message)
  } finally {
    statusLoading.value[loadingKey] = false
  }
}

async function removeProduct(productNumber) {
  if (!confirm('حذف المنتج من المخزون والتليجرام؟')) return
  try {
    const res = await fetch(`/api/products/${encodeURIComponent(productNumber)}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${auth.user?.token}`
      }
    })
    if (!res.ok) throw new Error('فشل الحذف')
    await load()
  } catch (e) {
    alert('خطأ أثناء الحذف: ' + e.message)
  }
}

function formatDate(iso) {
  if (!iso) return 'غير محدد';
  return new Date(iso).toLocaleString('ar-IQ', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  });
}

onMounted(load)
</script>

<template>
  <div class="inventory-page">
    <header class="ios-header">
      <h1>التوفر والمخزون</h1>
      <button @click="load" class="refresh-circular">
        <RefreshCw :class="{ 'spinning': loading }" :size="18" />
      </button>
    </header>

    <div class="search-section">
      <div class="search-bar">
        <input 
          v-model="searchQuery" 
          @input="handleSearch"
          type="text" 
          placeholder="بحث عن منتج، رقم، أو سيارة..."
        >
      </div>
    </div>

    <div v-if="loading && products.length === 0" class="loader">
      <RefreshCw class="spinning" />
    </div>

    <div v-else class="full-info-grid">
      <div v-for="p in products" :key="p._id" class="info-card card" :class="{ 'editing-mode': editingId === p._id }">
        <div class="card-image" @click="p.imageUrl && openImage(p.imageUrl)">
          <img v-if="p.imageUrl" :src="p.imageUrl" :alt="p.product_name">
          <div v-else class="no-image">
             <ImageIcon :size="48" :stroke-width="1" />
          </div>
          <div class="status-chip" :class="p.quantity > 0 ? 'available' : 'out'">
            {{ p.quantity > 0 ? 'متوفر' : 'نفذت' }}
          </div>
          <div class="id-tag">#{{ p.product_number }}</div>
        </div>

        <div class="card-content">
          <template v-if="editingId !== p._id">
            <div class="main-details">
              <h4 class="product-name">{{ p.product_name }}</h4>
              <p class="car-type">{{ p.car_name }}</p>
            </div>

            <div class="specs-grid">
              <div class="spec-item">
                <span class="s-label">رقم المنتج</span>
                <span class="s-value id-code">#{{ p.product_number }}</span>
              </div>
              <div class="spec-item">
                <span class="s-label">الكمية</span>
                <span class="s-value qty">{{ p.quantity }} قطع</span>
              </div>
              <div class="spec-item">
                <span class="s-label">سعر البيع</span>
                <span class="s-value price">{{ p.price_iqd.toLocaleString() }} <small>د.ع</small></span>
              </div>
              <div class="spec-item">
                <span class="s-label">سعر الجملة</span>
                <span class="s-value wholesale">{{ p.wholesale_price_iqd.toLocaleString() }} <small>د.ع</small></span>
              </div>
              <div class="spec-item full-width">
                <span class="s-label">آخر تحديث</span>
                <span class="s-value date">{{ formatDate(p.last_update) }}</span>
              </div>
            </div>

            <div class="card-actions-premium">
              <div class="sell-actions-v2">
                <button 
                  @click="updateStatus(p.product_number, 'sold_one')" 
                  class="btn-action sell-one"
                  :disabled="statusLoading[`${p.product_number}-sold_one`]"
                >
                   <span class="btn-icon">
                     <template v-if="statusLoading[`${p.product_number}-sold_one`]">⏳</template>
                     <template v-else>💰</template>
                   </span>
                   <div class="btn-text-content">
                     <span class="btn-title">{{ statusLoading[`${p.product_number}-sold_one`] ? 'جاري...' : 'بيع قطعة' }}</span>
                     <span class="btn-desc">-1 من المخزن</span>
                   </div>
                </button>
                <button 
                  @click="updateStatus(p.product_number, 'sold_all')" 
                  class="btn-action sell-all"
                  :disabled="statusLoading[`${p.product_number}-sold_all`]"
                >
                   <span class="btn-icon">
                     <template v-if="statusLoading[`${p.product_number}-sold_all`]">⏳</template>
                     <template v-else>🔥</template>
                   </span>
                   <div class="btn-text-content">
                     <span class="btn-title">{{ statusLoading[`${p.product_number}-sold_all`] ? 'جاري...' : 'بيع الكل' }}</span>
                     <span class="btn-desc">تصفية الكمية</span>
                   </div>
                </button>
              </div>
              <div class="management-actions">
                <button @click="startEditing(p)" class="btn-manage edit">تعديل البيانات</button>
                <button @click="removeProduct(p.product_number)" class="btn-manage delete">حذف نهائي</button>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="edit-form">
              <div class="edit-field-group">
                <label class="edit-label">رقم المنتج</label>
                <input v-model="editForm.product_number" class="edit-input" placeholder="رقم المنتج">
              </div>
              
              <div class="edit-field-group">
                <label class="edit-label">اسم المنتج</label>
                <input v-model="editForm.product_name" class="edit-input" placeholder="اسم المنتج">
              </div>
              
              <div class="edit-row">
                <div class="edit-field-group">
                  <label class="edit-label">السيارة</label>
                  <input v-model="editForm.car_name" class="edit-input" placeholder="السيارة">
                </div>
                <div class="edit-field-group">
                  <label class="edit-label">الموديل</label>
                  <input v-model="editForm.model_number" class="edit-input" placeholder="الموديل">
                </div>
              </div>
              
              <div class="edit-field-group">
                <label class="edit-label">النوع</label>
                <input v-model="editForm.type" class="edit-input" placeholder="مثلاً: كهربائيات">
              </div>
              
              <div class="edit-row">
                <div class="edit-field-group">
                  <label class="edit-label">الكمية</label>
                  <input v-model.number="editForm.quantity" type="number" class="edit-input" placeholder="الكمية">
                </div>
                <div class="edit-field-group">
                  <label class="edit-label">سعر البيع</label>
                  <input v-model="editForm.price_iqd" @input="e => formatInputPrice(e, 'price_iqd')" type="text" class="edit-input" placeholder="بيع">
                </div>
              </div>
              
              <div class="edit-field-group">
                <label class="edit-label">سعر الجملة</label>
                <input v-model="editForm.wholesale_price_iqd" @input="e => formatInputPrice(e, 'wholesale_price_iqd')" type="text" class="edit-input" placeholder="جملة">
              </div>
              
              <div class="edit-field-group">
                <label class="edit-label">تغيير الصورة (اختياري)</label>
                <input type="file" @change="e => editImageFile = e.target.files[0]" accept="image/*" class="edit-file-input">
              </div>
              
              <div class="edit-actions">
                <button @click="saveEdit" class="save-btn" :disabled="editLoading">
                  {{ editLoading ? 'جاري الحفظ...' : 'حفظ التعديلات' }}
                </button>
                <button @click="cancelEdit" class="cancel-btn">إلغاء</button>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>

  <!-- Image Modal -->
  <div v-if="showImageModal" class="image-modal-overlay" @click="closeImage">
    <div class="image-modal-content" @click.stop>
      <img :src="selectedImage" alt="Full view">
      <button class="close-modal-btn" @click="closeImage">
        <X :size="24" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.inventory-page {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px 40px;
}

.full-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
  padding-bottom: 60px;
}

.info-card {
  padding: 0 !important;
  display: flex;
  flex-direction: row;
  overflow: hidden;
  background: rgba(28, 28, 30, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  min-height: 200px;
  border-radius: 20px;
  transition: transform 0.3s ease, border-color 0.3s ease;
}

.info-card:hover {
  transform: translateY(-4px);
  border-color: rgba(10, 132, 255, 0.3);
}

.card-image {
  width: 160px;
  position: relative;
  background: #111;
  flex-shrink: 0;
}

@media (max-width: 1100px) {
  .full-info-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .inventory-page { padding: 16px; }
  .full-info-grid { grid-template-columns: 1fr; }
  .info-card { flex-direction: column; border-radius: 24px; }
  .card-image { width: 100%; height: 200px; }
}

.info-card:active {
  transform: scale(0.99);
  border-color: rgba(10, 132, 255, 0.5);
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s;
}

.card-image img:active {
  transform: scale(0.95);
}

.no-image {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
}

.status-chip {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 10px;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  font-weight: 700;
}
.status-chip.available { color: #30d158; border: 0.5px solid rgba(48, 209, 88, 0.3); }
.status-chip.out { color: #ff453a; border: 0.5px solid rgba(255, 69, 58, 0.3); }

.id-tag {
  position: absolute;
  bottom: 8px;
  right: 8px;
  font-size: 10px;
  color: white;
  opacity: 0.6;
  font-family: monospace;
}

.card-content {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.main-details { margin-bottom: 12px; }
.product-name { margin: 0 0 4px; font-size: 18px; font-weight: 700; }
.car-type { margin: 0; color: var(--system-gray); font-size: 14px; }

.specs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
}

.spec-item { display: flex; flex-direction: column; gap: 2px; }
.s-label { font-size: 11px; color: var(--system-gray); }
.s-value { font-size: 14px; font-weight: 600; }
.s-value.price { color: var(--system-blue); }
.s-value.wholesale { color: var(--system-green); }
.s-value.qty { color: var(--system-orange); }
.s-value.id-code { color: var(--system-gray); font-family: monospace; }
.s-value.date { font-size: 12px; opacity: 0.8; }

.spec-item.full-width {
  grid-column: span 2;
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 8px;
  margin-top: 4px;
}

.card-actions-premium {
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sell-actions-v2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  text-align: right;
  background: rgba(255,255,255,0.05);
}

.btn-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
}

.btn-action:active { 
  transform: scale(0.96); 
  background: rgba(255, 255, 255, 0.1);
}

.btn-action.sell-one { background: rgba(48, 209, 88, 0.15); border: 1px solid rgba(48, 209, 88, 0.3); }
.btn-action.sell-all { background: rgba(255, 69, 58, 0.15); border: 1px solid rgba(255, 69, 58, 0.3); }

.btn-icon { font-size: 20px; }
.btn-text-content { display: flex; flex-direction: column; }
.btn-title { font-weight: 800; font-size: 14px; color: white; }
.btn-desc { font-size: 10px; opacity: 0.6; color: white; }

.management-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.btn-manage {
  padding: 10px;
  border-radius: 12px;
  border: none;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.btn-manage.edit { background: rgba(255, 159, 10, 0.1); color: var(--system-orange); }
.btn-manage.delete { background: rgba(255, 69, 58, 0.05); color: var(--system-red); }

@media (max-width: 480px) {
  .info-card { 
    flex-direction: column; 
    border-radius: 28px;
    background: #1c1c1e;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  }
  .card-image { width: 100%; height: 220px; }
  .status-chip { top: 12px; right: 12px; padding: 6px 12px; font-size: 12px; }
  .card-content { padding: 20px; }
  .product-name { font-size: 22px; }
  .specs-grid { gap: 15px; padding: 15px; margin-bottom: 20px; }
  .sell-actions-v2 { grid-template-columns: 1fr; } /* Full width on mobile for selling buttons */
  .btn-action { padding: 16px; }
}

.edit-form { display: flex; flex-direction: column; gap: 12px; }

.edit-field-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.edit-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.edit-input { background: var(--system-tertiary-bg); border: 1px solid var(--border); padding: 10px 12px; border-radius: 8px; color: white; font-size: 14px; }
.edit-input:disabled { opacity: 0.5; cursor: not-allowed; }
.edit-input:focus { outline: none; border-color: var(--system-blue); }

.edit-file-input {
  background: var(--system-tertiary-bg);
  border: 1px solid var(--border);
  padding: 10px 12px;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
}

.edit-file-input::-webkit-file-upload-button {
  background: var(--system-blue);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  margin-left: 10px;
}

.edit-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.edit-actions { display: flex; gap: 10px; margin-top: 12px; }
.save-btn { flex: 2; background: var(--system-blue); color: white; border: none; padding: 8px; border-radius: 8px; font-weight: 700; }
.cancel-btn { flex: 1; background: var(--system-tertiary-bg); color: white; border: none; padding: 8px; border-radius: 8px; }

.editing-mode { border-color: var(--system-blue) !important; box-shadow: 0 0 15px rgba(10, 132, 255, 0.2); }

@media (max-width: 480px) {
  .info-card { flex-direction: column; }
  .card-image { width: 100%; height: 160px; }
}

.ios-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.refresh-circular { background: var(--system-secondary-bg); border: none; color: var(--system-blue); width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; }
.refresh-circular:active { transform: scale(0.9); opacity: 0.7; }

.search-section { 
  margin-bottom: 24px;
  padding: 0 4px;
}

.search-bar input { 
  width: 100%; 
  background: var(--system-secondary-bg); 
  border: 0.5px solid var(--border); 
  padding: 12px 16px; 
  border-radius: 12px; 
  color: white; 
  font-size: 15px; 
  outline: none;
  transition: all 0.2s;
}

.search-bar input:focus { 
  border-color: var(--system-blue);
  box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.1);
}

.spinning { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.image-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.2s ease;
}

.image-modal-content {
  width: 350px;
  height: 350px;
  background: #1c1c1e;
  border-radius: 20px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  animation: scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.image-modal-content img {
  width: 100%;
  height: 100%;
  object-fit: contain; /* Keeps ratio but fits in square box as requested? Or cover? user said 'square' */
  /* User said "open in a square shape". If the image is not square, cover might crop it. contain ensures it's fully visible. 
     But let's assume they want the VIEWPORT to be square. */
  object-fit: cover; 
}

.close-modal-btn {
  position: absolute;
  top: 15px;
  left: 15px;
  background: rgba(0,0,0,0.5);
  border: none;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }

</style>
