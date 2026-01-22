"""
Car Stock Management System - Hybrid Cloud Storage
نظام إدارة مخزون السيارات - تخزين هجين (تليجرام + ImgBB)
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import json
import os
import io
import base64
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import asyncio
from pathlib import Path
import hashlib
import secrets

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Car Stock - Hybrid Cloud", version="5.0.0")
security = HTTPBearer()

# Mount Static Files from Vue Build
# Path: ../web-frontend/dist
dist_path = Path(__file__).parent.parent / "web-frontend" / "dist"

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes stay same...

# Telegram Config
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ImgBB Config
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")
IMGBB_URL = "https://api.imgbb.com/1/upload"

# Cache file (فقط للفهرسة السريعة)
CACHE_FILE = "telegram_cache.json"

# Backup directory
BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

# Users & Permissions
USERS_FILE = "users.json"
SESSIONS_FILE = "sessions.json"

# User Roles
ROLES = {
    "admin": {
        "name": "مدير",
        "permissions": ["view", "add", "edit", "delete", "export", "import", "backup"]
    },
    "employee": {
        "name": "موظف",
        "permissions": ["view", "add", "edit", "export"]
    },
    "viewer": {
        "name": "عارض",
        "permissions": ["view"]
    }
}

# ================================
# Users & Authentication Management
# ================================

def load_users() -> dict:
    """تحميل المستخدمين"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # إنشاء مستخدم مدير افتراضي
    default_users = {
        "admin": {
            "username": "admin",
            "password": hashlib.sha256("admin123".encode()).hexdigest(),
            "role": "admin",
            "name": "المدير",
            "created_at": datetime.now().isoformat()
        }
    }
    save_users(default_users)
    return default_users

def save_users(users: dict):
    """حفظ المستخدمين"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_sessions() -> dict:
    """تحميل الجلسات النشطة"""
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                sessions = json.load(f)
                # حذف الجلسات المنتهية
                now = datetime.now()
                active_sessions = {
                    token: data for token, data in sessions.items()
                    if datetime.fromisoformat(data["expires_at"]) > now
                }
                if len(active_sessions) != len(sessions):
                    save_sessions(active_sessions)
                return active_sessions
        except:
            pass
    return {}

def save_sessions(sessions: dict):
    """حفظ الجلسات"""
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2, ensure_ascii=False)

def create_session(username: str, role: str) -> str:
    """إنشاء جلسة جديدة"""
    token = secrets.token_urlsafe(32)
    sessions = load_sessions()
    sessions[token] = {
        "username": username,
        "role": role,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
    }
    save_sessions(sessions)
    return token

def verify_session(token: str) -> Optional[dict]:
    """التحقق من الجلسة"""
    sessions = load_sessions()
    return sessions.get(token)

def check_permission(session: dict, permission: str) -> bool:
    """التحقق من الصلاحية"""
    role = session.get("role")
    if not role or role not in ROLES:
        return False
    return permission in ROLES[role]["permissions"]

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """الحصول على المستخدم الحالي"""
    token = credentials.credentials
    session = verify_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="جلسة غير صالحة أو منتهية")
    return session

def require_permission(permission: str):
    """التحقق من صلاحية معينة"""
    async def permission_checker(session: dict = Depends(get_current_user)):
        if not check_permission(session, permission):
            raise HTTPException(
                status_code=403, 
                detail=f"ليس لديك صلاحية {permission}"
            )
        return session
    return permission_checker

# ================================
# Cache Management
# ================================

# ================================
# Database Abstraction (Convex)
# ================================

from convex import ConvexClient

CONVEX_URL = os.getenv("VITE_CONVEX_URL", "") or os.getenv("CONVEX_URL", "")
# Strip quotes if necessary
if CONVEX_URL.startswith('"') and CONVEX_URL.endswith('"'):
    CONVEX_URL = CONVEX_URL[1:-1]
    
# Fallback to hardcoded if env missing (useful for dev)
if not CONVEX_URL:
    print("Warning: CONVEX_URL not set in env, trying .env file manually")
    CONVEX_URL = "https://flexible-lion-950.convex.cloud" # Adjust if needed

try:
    convex_client = ConvexClient(CONVEX_URL)
except Exception as e:
    print(f"Error initializing Convex: {e}")
    convex_client = None

def normalize_pn(pn):
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    western_digits = "0123456789"
    res = str(pn)
    for a, w in zip(arabic_digits, western_digits):
        res = res.replace(a, w)
    return res

def load_cache() -> dict:
    """تحميل المنتجات من Convex"""
    if not convex_client:
        return {}
    try:
        # Get all products without filter to avoid issues with some Convex clients
        products = convex_client.query("products:getProducts", {})
        
        def normalize_pn(pn):
            arabic_digits = "٠١٢٣٤٥٦٧٨٩"
            western_digits = "0123456789"
            res = str(pn)
            for a, w in zip(arabic_digits, western_digits):
                res = res.replace(a, w)
            return res

        # Convert list to dict keyed by normalized product_number
        return {normalize_pn(p.get('product_number', '')): p for p in products if p.get('product_number') is not None}
    except Exception as e:
        print(f"Convex Query Error: {e}")
        return {}

def save_cache(data: dict):
    pass

def add_product_to_db(product: dict):
    if not convex_client: return
    p = {k:v for k,v in product.items() if k not in ["_id", "_creationTime"] and v is not None}
    # Ensure quantity and prices are numbers
    if "quantity" in p: p["quantity"] = int(p["quantity"])
    if "price_iqd" in p: p["price_iqd"] = float(p["price_iqd"])
    if "wholesale_price_iqd" in p: p["wholesale_price_iqd"] = float(p["wholesale_price_iqd"])
    convex_client.mutation("products:addProduct", p)

def update_product_in_db(product_number: str, updates: dict):
    if not convex_client: return
    try:
        all_products = convex_client.query("products:getProducts", {}) 
        # Safely find target using .get()
        target = next((p for p in all_products if str(p.get('product_number')) == str(product_number)), None)
        
        if target:
            patch = {}
            # Only take valid fields for the updates object in Convex TS
            # EXCLUDING product_number because it's the identifier and might cause validation errors if sent in updates
            valid_fields = ["product_name", "car_name", "model_number", "type", "quantity", "price_iqd", "wholesale_price_iqd", "image", "status", "last_update", "message_id"]
            for k in valid_fields:
                if k in updates and updates[k] is not None:
                    val = updates[k]
                    if k == "quantity": val = int(val)
                    if k in ["price_iqd", "wholesale_price_iqd"]: val = float(val)
                    patch[k] = val
            
            # Use target["_id"] directly, assuming it's a string ID or the client handles it
            convex_client.mutation("products:updateProduct", {"id": target["_id"], "updates": patch})
    except Exception as e:
        print(f"Error in update_product_in_db: {e}")
        raise e

def delete_product_from_db(product_number: str):
    if not convex_client: return
    try:
        all_products = convex_client.query("products:getProducts", {}) 
        target = next((p for p in all_products if str(p.get('product_number')) == str(product_number)), None)
        if target:
            convex_client.mutation("products:deleteProduct", {"id": target["_id"]})
    except Exception as e:
        print(f"Error in delete_product_from_db: {e}")
        raise e


# ================================
# Image Upload to ImgBB
# ================================

async def upload_image_to_imgbb(image_content: bytes) -> str:
    """رفع الصورة إلى ImgBB وإرجاع الرابط"""
    
    if not IMGBB_API_KEY or IMGBB_API_KEY == "ضع_مفتاح_imgbb_هنا":
        raise HTTPException(status_code=500, detail="ImgBB API Key غير مُعد. راجع ملف .env")
    
    try:
        # تحويل الصورة إلى base64
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                IMGBB_URL,
                data={
                    "key": IMGBB_API_KEY,
                    "image": image_base64
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result["data"]["url"]
                else:
                    raise Exception(f"ImgBB Error: {result.get('error', {}).get('message', 'Unknown error')}")
            else:
                raise Exception(f"ImgBB HTTP Error: {response.status_code}")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل رفع الصورة: {str(e)}")

# ================================
# Telegram Operations
# ================================

async def send_to_telegram(product: dict, image_url: str = None, message_id: int = None):
    """إرسال المنتج للتليجرام أو تحديثه وإرجاع message_id"""
    
    caption = f"""
🔧 <b>{product['product_name']}</b>
━━━━━━━━━━━━━━━━
🚗 السيارة: <b>{product['car_name']}</b>
🔢 الموديل: {product.get('model_number', 'غير محدد')}
🏷️ الرقم: <code>{product['product_number']}</code>
📂 النوع: {product['type']}
📦 الكمية: <b>{product['quantity']}</b>
📊 الحالة: <b>{product.get('status', 'غير محدد')}</b>
━━━━━━━━━━━━━━━━
💰 السعر: <b>{float(product['price_iqd']):,.0f} IQD</b>
📦 الجملة: <b>{float(product['wholesale_price_iqd']):,.0f} IQD</b>
━━━━━━━━━━━━━━━━
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    if image_url:
        caption += f"\n🖼️ <a href='{image_url}'>عرض الصورة</a>"

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            if message_id:
                # تحديث رسالة موجودة
                resp = await client.post(
                    f"{TG_URL}/editMessageText",
                    json={
                        "chat_id": CHAT_ID,
                        "message_id": message_id,
                        "text": caption,
                        "parse_mode": "HTML"
                    }
                )
            else:
                # إرسال رسالة جديدة
                resp = await client.post(
                    f"{TG_URL}/sendMessage",
                    json={"chat_id": CHAT_ID, "text": caption, "parse_mode": "HTML"}
                )
            
            if resp.status_code == 200:
                result = resp.json()["result"]
                # In editMessageText, result is the Message object or True
                return message_id if message_id else result["message_id"]
            else:
                # If editing failed (message deleted?), send new
                if message_id:
                    return await send_to_telegram(product, image_url)
                raise Exception(f"Telegram API Error: {resp.text}")
                
        except Exception as e:
            print(f"Telegram Error: {e}")
            return None

async def delete_from_telegram(message_id: int):
    """حذف رسالة من التليجرام"""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            await client.post(
                f"{TG_URL}/deleteMessage",
                json={"chat_id": CHAT_ID, "message_id": message_id}
            )
        except:
            pass

# ================================
# API Endpoints
# ================================

@app.get("/api/health")
async def health_check_api():
    return {
        "status": "online",
        "version": "5.0.0",
        "telegram": bool(BOT_TOKEN and CHAT_ID)
    }

# ================================
# Authentication Endpoints
# ================================

@app.post("/api/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """تسجيل الدخول"""
    users = load_users()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user_data = None
    
    # Check local first
    if username in users:
        user = users[username]
        if user["password"] == password_hash:
            user_data = {
                "username": user["username"],
                "name": user["name"],
                "role": user["role"]
            }
    
    # If not found or wrong password local, check Convex
    if not user_data and convex_client:
        try:
            # Query users from Convex
            all_users = convex_client.query("users:listUsers")
            convex_user = next((u for u in all_users if u.get("username") == username), None)
            if convex_user and convex_user.get("password") == password_hash:
                user_data = {
                    "username": convex_user["username"],
                    "name": convex_user["name"],
                    "role": convex_user.get("role", "employee")
                }
        except Exception as e:
            print(f"Convex Auth Error: {e}")

    if not user_data:
        raise HTTPException(status_code=401, detail="اسم المستخدم أو كلمة المرور غير صحيحة")
    
    # إنشاء جلسة
    token = create_session(user_data["username"], user_data["role"])
    
    return {
        "token": token,
        "user": {
            "username": user_data["username"],
            "name": user_data["name"],
            "role": user_data["role"],
            "role_name": ROLES.get(user_data["role"], {}).get("name", "موظف"),
            "permissions": ROLES.get(user_data["role"], {}).get("permissions", ROLES["employee"]["permissions"])
        }
    }

@app.post("/api/auth/logout")
async def logout(session: dict = Depends(get_current_user)):
    """تسجيل الخروج"""
    # حذف الجلسة
    sessions = load_sessions()
    sessions = {k: v for k, v in sessions.items() if v.get("username") != session["username"]}
    save_sessions(sessions)
    
    return {"message": "تم تسجيل الخروج بنجاح"}

@app.get("/api/auth/me")
async def get_me(session: dict = Depends(get_current_user)):
    """الحصول على معلومات المستخدم الحالي"""
    users = load_users()
    user = users.get(session["username"])
    
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    
    return {
        "username": user["username"],
        "name": user["name"],
        "role": user["role"],
        "role_name": ROLES[user["role"]]["name"],
        "permissions": ROLES[user["role"]]["permissions"]
    }

@app.get("/api/auth/roles")
async def get_roles():
    """الحصول على الأدوار المتاحة"""
    return ROLES

# ================================
# User Management (Admin Only)
# ================================

@app.get("/api/users")
async def list_users(session: dict = Depends(require_permission("backup"))):
    """قائمة المستخدمين (للمدير فقط)"""
    users = load_users()
    return [
        {
            "username": u["username"],
            "name": u["name"],
            "role": u["role"],
            "role_name": ROLES[u["role"]]["name"],
            "created_at": u.get("created_at")
        }
        for u in users.values()
    ]

@app.post("/api/users")
async def create_user(
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    role: str = Form(...),
    session: dict = Depends(require_permission("backup"))
):
    """إنشاء مستخدم جديد (للمدير فقط)"""
    if role not in ROLES:
        raise HTTPException(status_code=400, detail="دور غير صالح")
    
    users = load_users()
    
    if username in users:
        raise HTTPException(status_code=400, detail="اسم المستخدم موجود مسبقاً")
    
    users[username] = {
        "username": username,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "role": role,
        "name": name,
        "created_at": datetime.now().isoformat()
    }
    
    save_users(users)
    
    return {
        "message": "تم إنشاء المستخدم بنجاح",
        "user": {
            "username": username,
            "name": name,
            "role": role,
            "role_name": ROLES[role]["name"]
        }
    }

@app.delete("/api/users/{username}")
async def delete_user(
    username: str,
    session: dict = Depends(require_permission("backup"))
):
    """حذف مستخدم (للمدير فقط)"""
    if username == "admin":
        raise HTTPException(status_code=400, detail="لا يمكن حذف المدير الرئيسي")
    
    users = load_users()
    
    if username not in users:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    
    del users[username]
    save_users(users)
    
    return {"message": "تم حذف المستخدم بنجاح"}

@app.get("/api/products")
async def get_products(
    search: str = None,
    car_name: str = None,
    product_type: str = None,
    status: str = None,
    min_price: float = None,
    max_price: float = None,
    sort_by: str = "last_update",
    order: str = "desc",
    session: dict = Depends(get_current_user)
):
    """جلب جميع المنتجات مع فلترة وبحث متقدم"""
    cache = load_cache()
    products = list(cache.values())
    
    # تطبيق الفلاتر
    if search:
        search_lower = search.lower()
        products = [p for p in products if 
            search_lower in p.get("product_name", "").lower() or
            search_lower in p.get("car_name", "").lower() or
            search_lower in p.get("product_number", "").lower() or
            search_lower in p.get("type", "").lower() or
            search_lower in p.get("model_number", "").lower()
        ]
    
    if car_name:
        products = [p for p in products if car_name.lower() in p.get("car_name", "").lower()]
    
    if product_type:
        products = [p for p in products if product_type.lower() in p.get("type", "").lower()]
    
    if status:
        if status == "available":
            products = [p for p in products if p.get("quantity", 0) > 0]
        elif status == "out_of_stock":
            products = [p for p in products if p.get("quantity", 0) == 0]
    
    if min_price is not None:
        products = [p for p in products if p.get("price_iqd", 0) >= min_price]
    
    if max_price is not None:
        products = [p for p in products if p.get("price_iqd", 0) <= max_price]
    
    # الترتيب
    reverse = order == "desc"
    if sort_by == "price":
        products.sort(key=lambda x: x.get("price_iqd", 0), reverse=reverse)
    elif sort_by == "quantity":
        products.sort(key=lambda x: x.get("quantity", 0), reverse=reverse)
    elif sort_by == "name":
        products.sort(key=lambda x: x.get("product_name", ""), reverse=reverse)
    else:  # last_update
        products.sort(key=lambda x: x.get("last_update", ""), reverse=reverse)
    
    return products

@app.get("/api/stats")
async def get_statistics(session: dict = Depends(get_current_user)):
    """إحصائيات شاملة للوحة التحكم"""
    cache = load_cache()
    products = list(cache.values())
    
    total_products = len(products)
    available_products = sum(1 for p in products if p.get("quantity", 0) > 0)
    out_of_stock = total_products - available_products
    
    total_value = sum(p.get("price_iqd", 0) * p.get("quantity", 0) for p in products)
    total_items = sum(p.get("quantity", 0) for p in products)
    
    # حسب النوع
    by_type = {}
    for p in products:
        ptype = p.get("type", "غير محدد")
        if ptype not in by_type:
            by_type[ptype] = {"count": 0, "quantity": 0, "value": 0}
        by_type[ptype]["count"] += 1
        by_type[ptype]["quantity"] += p.get("quantity", 0)
        by_type[ptype]["value"] += p.get("price_iqd", 0) * p.get("quantity", 0)
    
    # حسب السيارة
    by_car = {}
    for p in products:
        car = p.get("car_name", "غير محدد")
        if car not in by_car:
            by_car[car] = {"count": 0, "quantity": 0}
        by_car[car]["count"] += 1
        by_car[car]["quantity"] += p.get("quantity", 0)
    
    # أكثر المنتجات مبيعاً (الأقل كمية من الأصلي)
    top_selling = sorted(
        [p for p in products if p.get("original_quantity", 0) > 0],
        key=lambda x: (x.get("original_quantity", 0) - x.get("quantity", 0)),
        reverse=True
    )[:10]
    
    return {
        "overview": {
            "total_products": total_products,
            "available_products": available_products,
            "out_of_stock": out_of_stock,
            "total_value": total_value,
            "total_items": total_items,
            "average_price": total_value / total_items if total_items > 0 else 0
        },
        "by_type": by_type,
        "by_car": dict(sorted(by_car.items(), key=lambda x: x[1]["count"], reverse=True)[:10]),
        "top_selling": [
            {
                "product_number": p.get("product_number"),
                "product_name": p.get("product_name"),
                "sold": p.get("original_quantity", 0) - p.get("quantity", 0),
                "remaining": p.get("quantity", 0)
            }
            for p in top_selling
        ],
        "low_stock": [
            {
                "product_number": p.get("product_number"),
                "product_name": p.get("product_name"),
                "quantity": p.get("quantity", 0)
            }
            for p in sorted(products, key=lambda x: x.get("quantity", 0))[:10]
            if p.get("quantity", 0) > 0 and p.get("quantity", 0) < 5
        ]
    }

@app.post("/api/products")
async def create_product(
    product_number: Optional[str] = Form(None),
    product_name: str = Form(...),
    car_name: str = Form(...),
    model_number: str = Form(""),
    product_type: str = Form("قطعة"),
    quantity: int = Form(1),
    price_iqd: str = Form(...),
    wholesale_price_iqd: str = Form(...),
    image: Optional[UploadFile] = File(None),
    session: dict = Depends(get_current_user)
):
    """إضافة منتج جديد - الصور في ImgBB والبيانات في التليجرام"""
    
    # تحويل الأسعار من نص إلى رقم (مع إزالة الفواصل إن وجدت)
    try:
        price_iqd = float(str(price_iqd).replace(',', ''))
        wholesale_price_iqd = float(str(wholesale_price_iqd).replace(',', ''))
    except Exception as e:
        raise HTTPException(status_code=400, detail="صيغة السعر غير صحيحة")
    
    if not BOT_TOKEN or not CHAT_ID:
        raise HTTPException(status_code=500, detail="التليجرام غير مُعد. راجع ملف .env")
    
    cache = load_cache()
    
    if product_number:
        if product_number in cache:
            raise HTTPException(status_code=400, detail="رقم المنتج موجود مسبقاً")
    else:
        # Generate a unique product number if not provided
        import random
        import string
        date_str = datetime.now().strftime('%Y%m%d')
        rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        product_number = f"PN-{date_str}-{rand_str}"
    
    # رفع الصورة إلى ImgBB
    image_url = None
    if image:
        image_content = await image.read()
        image_url = await upload_image_to_imgbb(image_content)
    
    # إنشاء بيانات المنتج
    product = {
        "product_number": product_number,
        "product_name": product_name,
        "car_name": car_name,
        "model_number": model_number,
        "type": product_type,
        "quantity": quantity,
        "original_quantity": quantity,
        "price_iqd": price_iqd,
        "wholesale_price_iqd": wholesale_price_iqd,
        "status": "متوفر",
        "image": image_url,
        "last_update": datetime.now().isoformat()
    }
    
    # إرسال للتليجرام
    msg_id = await send_to_telegram(product, image_url)
    
    # حفظ المعرفات 
    product["message_id"] = msg_id
    
    # حفظ في Convex
    add_product_to_db(product)
    
    return product

@app.get("/image/{image_id}")
async def get_image(image_id: str):
    """إعادة توجيه إلى رابط الصورة في ImgBB"""
    
    # البحث عن المنتج الذي يحتوي على هذه الصورة
    cache = load_cache()
    
    for product in cache.values():
        if product.get("image") and image_id in product["image"]:
            return RedirectResponse(url=product["image"])
    
    raise HTTPException(status_code=404, detail="الصورة غير موجودة")

@app.post("/api/update-status/{product_number:path}")
async def update_product_status(
    product_number: str, 
    action: str = Query(...),
    session: dict = Depends(get_current_user)
):
    """تحديث حالة المنتج (تم بيع، تم بيع بالكامل، نفذ)"""
    product_number = normalize_pn(product_number)
    cache = load_cache()
    
    if product_number not in cache:
        raise HTTPException(status_code=404, detail="المنتج غير موجود")
    
    product = cache[product_number]
    
    if action == "sold_one":
        if product["quantity"] > 0:
            product["quantity"] -= 1
            product["status"] = "متوفر" if product["quantity"] > 0 else "نفذ"
    elif action == "sold_all":
        product["quantity"] = 0
        product["status"] = "نفذ"
    
    product["last_update"] = datetime.now().isoformat()
    
    try:
        update_product_in_db(product_number, product)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في قاعدة البيانات: {str(e)}")
    
    msg_id = product.get("message_id")
    if msg_id:
        try:
            await send_to_telegram(product, product.get("image"), message_id=msg_id)
        except: pass
            
    return product

@app.patch("/api/products/{product_number:path}")
async def update_product(
    product_number: str,
    product_name: str = Form(None),
    car_name: str = Form(None),
    model_number: str = Form(None),
    product_type: str = Form(None),
    quantity: int = Form(None),
    price_iqd: str = Form(None),
    wholesale_price_iqd: str = Form(None),
    new_product_number: Optional[str] = Form(None, alias="product_number"),
    image: Optional[UploadFile] = File(None),
    session: dict = Depends(get_current_user)
):
    """تحديث منتج موجود"""
    product_number = normalize_pn(product_number)
    if new_product_number:
        new_product_number = normalize_pn(new_product_number)
    
    # تحويل الأسعار من نص إلى رقم (مع إزالة الفواصل إن وجدت)
    try:
        if price_iqd is not None:
            price_iqd = float(str(price_iqd).replace(',', ''))
        if wholesale_price_iqd is not None:
            wholesale_price_iqd = float(str(wholesale_price_iqd).replace(',', ''))
    except Exception as e:
        raise HTTPException(status_code=400, detail="صيغة السعر غير صحيحة")
    cache = load_cache()
    
    if product_number not in cache:
        raise HTTPException(status_code=404, detail="المنتج غير موجود")
    
    product = cache[product_number]
    
    # تحديث الحقول المرسلة فقط
    if product_name is not None:
        product["product_name"] = product_name
    if car_name is not None:
        product["car_name"] = car_name
    if model_number is not None:
        product["model_number"] = model_number
    if product_type is not None:
        product["type"] = product_type
    if quantity is not None:
        product["quantity"] = quantity
        product["status"] = "متوفر" if quantity > 0 else "نفذ"
    if price_iqd is not None:
        product["price_iqd"] = price_iqd
    if wholesale_price_iqd is not None:
        product["wholesale_price_iqd"] = wholesale_price_iqd
    
    # Update product number if changed
    if new_product_number and new_product_number != product_number:
        if new_product_number in cache:
            raise HTTPException(status_code=400, detail="رقم المنتج الجديد موجود مسبقاً")
        product["product_number"] = new_product_number
    
    # تحديث الصورة إذا تم رفع صورة جديدة
    if image:
        image_content = await image.read()
        image_url = await upload_image_to_imgbb(image_content)
        product["image"] = image_url
        
    product["last_update"] = datetime.now().isoformat()
    
    # Save to Convex
    # Construct update dict
    # Note: 'product' is the full object from cache (which we loaded from Convex via load_cache)
    # We just need to pass the changed fields or the full object.
    # updateProduct mutation in TS handles partial updates if we passed just ID and fields.
    # Here we are calling a wrapper that calls TS mutation.
    
    update_product_in_db(product_number, product)
    
    # Update on Telegram
    msg_id = product.get("message_id")
    if msg_id:
        try:
            await send_to_telegram(product, product.get("image"), message_id=msg_id)
        except Exception as e:
            print(f"Telegram Update Error: {e}")
    
    return product

@app.get("/api/settings")
async def get_settings(session: dict = Depends(require_permission("backup"))):
    """جلب إعدادات النظام (للمدير فقط)"""
    return {
        "telegram_bot_token": BOT_TOKEN[:10] + "..." if BOT_TOKEN else None,
        "telegram_chat_id": CHAT_ID,
        "imgbb_api_key": IMGBB_API_KEY[:5] + "..." if IMGBB_API_KEY else None,
        "version": "5.0.0",
        "convex_url": CONVEX_URL
    }

@app.post("/api/settings")
async def update_settings(
    bot_token: str = Form(None),
    chat_id: str = Form(None),
    imgbb_key: str = Form(None),
    session: dict = Depends(require_permission("backup"))
):
    """تحديث إعدادات النظام (للمدير فقط)"""
    # Note: In a real app, we'd write to .env or a config file.
    # For this demo/setup, we will update the global variables.
    global BOT_TOKEN, CHAT_ID, IMGBB_API_KEY, TG_URL
    
    if bot_token:
        BOT_TOKEN = bot_token
        TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
    if chat_id:
        CHAT_ID = chat_id
    if imgbb_key:
        IMGBB_API_KEY = imgbb_key
        
    return {"message": "تم تحديث الإعدادات بنجاح"}



@app.delete("/api/products/{product_number:path}")
async def delete_product(
    product_number: str,
    session: dict = Depends(get_current_user)
):
    """حذف منتج - يُحذف من التليجرام والكاش"""
    product_number = normalize_pn(product_number)
    cache = load_cache()
    
    if product_number not in cache:
        raise HTTPException(status_code=404, detail="المنتج غير موجود")
    
    product = cache[product_number]
    
    # حذف من التليجرام
    if product.get("message_id"):
        await delete_from_telegram(product["message_id"])
    
    # حذف من Convex
    delete_product_from_db(product_number)
    
    return {"status": "deleted", "product_number": product_number}

@app.get("/api/health")
async def health_check():
    """فحص الاتصال بالتليجرام و ImgBB"""
    
    status = {
        "telegram": {"status": "not_configured"},
        "imgbb": {"status": "not_configured"}
    }
    
    # Check Telegram
    if BOT_TOKEN and CHAT_ID:
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.get(f"{TG_URL}/getMe")
                if resp.status_code == 200:
                    bot_info = resp.json()["result"]
                    status["telegram"] = {
                        "status": "ok",
                        "bot_username": bot_info.get("username"),
                        "bot_name": bot_info.get("first_name"),
                        "chat_id": CHAT_ID
                    }
            except:
                status["telegram"] = {"status": "error", "message": "فشل الاتصال"}
    
    # Check ImgBB
    if IMGBB_API_KEY and IMGBB_API_KEY != "ضع_مفتاح_imgbb_هنا":
        status["imgbb"] = {"status": "ok", "api_key_configured": True}
    
    return status

# ================================
# Automatic Backup System
# ================================

def create_backup(backup_type: str = "manual"):
    """إنشاء نسخة احتياطية مرتبة ومنسقة"""
    try:
        cache = load_cache()
        
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        backup_data = {
            "backup_info": {
                "version": "5.0.0",
                "backup_type": backup_type,
                "backup_date": now.isoformat(),
                "total_products": len(cache),
                "created_by": "Auto Backup System"
            },
            "statistics": {
                "total_value": sum(p.get("price_iqd", 0) for p in cache.values()),
                "total_wholesale_value": sum(p.get("wholesale_price_iqd", 0) for p in cache.values()),
                "products_by_type": {}
            },
            "products": dict(sorted(cache.items()))
        }
        
        # إحصائيات حسب النوع
        for product in cache.values():
            ptype = product.get("type", "غير محدد")
            backup_data["statistics"]["products_by_type"][ptype] = \
                backup_data["statistics"]["products_by_type"].get(ptype, 0) + 1
        
        # حفظ النسخة الاحتياطية محلياً
        filename = f"backup_{backup_type}_{timestamp}.json"
        filepath = os.path.join(BACKUP_DIR, filename)
        
        json_content = json.dumps(backup_data, indent=2, ensure_ascii=False, sort_keys=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_content)
        
        # حفظ النسخة في Convex (Cloud)
        if convex_client:
            try:
                convex_client.mutation("backups:createBackup", {
                    "filename": filename,
                    "data": json_content,
                    "total_products": len(cache),
                    "type": backup_type
                })
                # الحفاظ على آخر 20 نسخة فقط لتوفير المساحة
                convex_client.mutation("backups:deleteOldBackups", {"keepCount": 20})
            except Exception as ex:
                print(f"Cloud Backup Error: {ex}")
        
        # إرسال للتليجرام
        if BOT_TOKEN and CHAT_ID:
            asyncio.create_task(send_backup_notification(backup_type, len(cache), filepath))
        
        return filepath
        
    except Exception as e:
        print(f"Backup Error: {e}")
        return None

async def send_backup_notification(backup_type: str, total_products: int, filepath: str):
    """إرسال إشعار النسخة الاحتياطية للتليجرام"""
    try:
        message = f"""
🔄 <b>نسخة احتياطية تلقائية</b>
━━━━━━━━━━━━━━━━
📋 النوع: {backup_type}
📦 عدد المنتجات: {total_products}
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━
✅ تم الحفظ بنجاح
"""
        
        async with httpx.AsyncClient(timeout=30) as client:
            # إرسال الرسالة
            await client.post(
                f"{TG_URL}/sendMessage",
                json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
            )
            
            # إرسال الملف
            with open(filepath, "rb") as f:
                files = {"document": (os.path.basename(filepath), f, "application/json")}
                await client.post(
                    f"{TG_URL}/sendDocument",
                    data={"chat_id": CHAT_ID, "caption": "📎 ملف النسخة الاحتياطية"},
                    files=files
                )
    except Exception as e:
        print(f"Notification Error: {e}")

def cleanup_old_backups(days: int = 30):
    """حذف النسخ الاحتياطية القديمة"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith("backup_") and filename.endswith(".json"):
                filepath = os.path.join(BACKUP_DIR, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_date:
                    os.remove(filepath)
                    print(f"Deleted old backup: {filename}")
    except Exception as e:
        print(f"Cleanup Error: {e}")

@app.on_event("startup")
async def startup_event():
    """تشغيل المهام التلقائية عند بدء السيرفر"""
    asyncio.create_task(auto_backup_scheduler())

async def auto_backup_scheduler():
    """جدولة النسخ الاحتياطية التلقائية"""
    last_daily_backup = None
    last_weekly_backup = None
    
    while True:
        try:
            now = datetime.now()
            
            # نسخة احتياطية يومية (كل يوم الساعة 2 صباحاً)
            if last_daily_backup != now.date() and now.hour == 2:
                create_backup("daily")
                last_daily_backup = now.date()
                print(f"Daily backup created: {now}")
            
            # نسخة احتياطية أسبوعية (كل يوم جمعة الساعة 3 صباحاً)
            week_num = now.isocalendar()[1]
            if last_weekly_backup != week_num and now.weekday() == 4 and now.hour == 3:
                create_backup("weekly")
                last_weekly_backup = week_num
                cleanup_old_backups(30)  # حذف النسخ الأقدم من 30 يوم
                print(f"Weekly backup created: {now}")
            
            # انتظر ساعة قبل الفحص التالي
            await asyncio.sleep(3600)
            
        except Exception as e:
            print(f"Scheduler Error: {e}")
            await asyncio.sleep(3600)

@app.post("/api/backup/manual")
async def create_manual_backup(session: dict = Depends(get_current_user)):
    """إنشاء نسخة احتياطية يدوية"""
    filepath = create_backup("manual")
    
    if filepath:
        return {
            "status": "success",
            "message": "تم إنشاء النسخة الاحتياطية بنجاح",
            "filepath": filepath,
            "filename": os.path.basename(filepath)
        }
    else:
        raise HTTPException(status_code=500, detail="فشل إنشاء النسخة الاحتياطية")

@app.get("/api/backups/list")
async def list_backups(session: dict = Depends(get_current_user)):
    """عرض قائمة النسخ الاحتياطية"""
    try:
        backups = []
        
        for filename in sorted(os.listdir(BACKUP_DIR), reverse=True):
            if filename.startswith("backup_") and filename.endswith(".json"):
                filepath = os.path.join(BACKUP_DIR, filename)
                file_stat = os.stat(filepath)
                
                backups.append({
                    "filename": filename,
                    "size": file_stat.st_size,
                    "created": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "type": filename.split("_")[1] if len(filename.split("_")) > 1 else "unknown"
                })
        
        return {
            "total_backups": len(backups),
            "backups": backups
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في قراءة النسخ الاحتياطية: {str(e)}")

# ================================
# Smart Backup & Restore System
# ================================

@app.get("/api/export")
async def export_data(session: dict = Depends(require_permission("export"))):
    """تصدير جميع البيانات (نسخة احتياطية ذكية ومرتبة)"""
    cache = load_cache()
    
    now = datetime.now()
    
    backup = {
        "backup_info": {
            "version": "5.0.0",
            "export_type": "manual",
            "export_date": now.isoformat(),
            "total_products": len(cache),
            "exported_by": "User"
        },
        "statistics": {
            "total_value": sum(p.get("price_iqd", 0) for p in cache.values()),
            "total_wholesale_value": sum(p.get("wholesale_price_iqd", 0) for p in cache.values()),
            "products_by_type": {},
            "products_by_location": {}
        },
        "products": dict(sorted(cache.items()))
    }
    
    # إحصائيات حسب النوع
    for product in cache.values():
        ptype = product.get("type", "غير محدد")
        backup["statistics"]["products_by_type"][ptype] = \
            backup["statistics"]["products_by_type"].get(ptype, 0) + 1
        
        location = product.get("location", "غير محدد")
        backup["statistics"]["products_by_location"][location] = \
            backup["statistics"]["products_by_location"].get(location, 0) + 1
    
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=backup,
        headers={
            "Content-Disposition": f"attachment; filename=car_stock_backup_{now.strftime('%Y%m%d_%H%M%S')}.json"
        }
    )

@app.post("/api/import")
async def import_data(
    file: UploadFile = File(...),
    session: dict = Depends(require_permission("import"))
):
    """استيراد البيانات بذكاء (يتجنب التكرار والخسارة)"""
    
    try:
        # قراءة الملف
        content = await file.read()
        imported_data = json.loads(content.decode('utf-8'))
        
        # التحقق من صحة البيانات
        if "products" not in imported_data:
            raise HTTPException(status_code=400, detail="ملف غير صالح - لا يحتوي على بيانات منتجات")
        
        cache = load_cache()
        
        stats = {
            "total_imported": 0,
            "new_products": 0,
            "skipped_duplicates": 0,
            "updated_products": 0,
            "errors": []
        }
        
        imported_products = imported_data["products"]
        
        for product_number, product_data in imported_products.items():
            try:
                stats["total_imported"] += 1
                
                if product_number in cache:
                    # المنتج موجود - نتحقق من التحديث
                    existing = cache[product_number]
                    existing_date = existing.get("last_update", "")
                    new_date = product_data.get("last_update", "")
                    
                    if new_date > existing_date:
                        # البيانات المستوردة أحدث
                        cache[product_number] = product_data
                        stats["updated_products"] += 1
                    else:
                        # البيانات الحالية أحدث - نتجاهل
                        stats["skipped_duplicates"] += 1
                else:
                    # منتج جديد
                    cache[product_number] = product_data
                    stats["new_products"] += 1
                    
            except Exception as e:
                stats["errors"].append({
                    "product_number": product_number,
                    "error": str(e)
                })
        
        # حفظ البيانات المحدثة
        save_cache(cache)
        
        return {
            "status": "success",
            "message": "تم الاستيراد بنجاح",
            "statistics": stats
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="ملف JSON غير صالح")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الاستيراد: {str(e)}")


async def sync_from_telegram():
    """مزامنة البيانات من قناة التليجرام (استرجاع ذكي)"""
    
    if not BOT_TOKEN or not CHAT_ID:
        raise HTTPException(status_code=500, detail="التليجرام غير مُعد")
    
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            # جلب آخر 100 رسالة من القناة
            resp = await client.get(
                f"{TG_URL}/getUpdates",
                params={"limit": 100}
            )
            
            if resp.status_code != 200:
                raise Exception("فشل الاتصال بالتليجرام")
            
            updates = resp.json().get("result", [])
            
            cache = load_cache()
            synced_count = 0
            
            for update in updates:
                message = update.get("message", {})
                if message.get("chat", {}).get("id") == int(CHAT_ID):
                    # استخراج البيانات من caption
                    caption = message.get("caption", "")
                    # يمكن تطوير parser ذكي هنا
                    synced_count += 1
            
            return {
                "status": "success",
                "synced_messages": synced_count,
                "total_products": len(cache)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"خطأ في المزامنة: {str(e)}")

@app.get("/api/backup-status")
async def backup_status(session: dict = Depends(get_current_user)):
    """حالة النسخ الاحتياطي"""
    cache = load_cache()
    
    if not cache:
        return {
            "has_backup": False,
            "total_products": 0,
            "last_update": None
        }
    
    # إيجاد آخر تحديث
    last_update = max(
        (p.get("last_update") for p in cache.values() if p.get("last_update")),
        default=None
    )
    
    return {
        "has_backup": True,
        "total_products": len(cache),
        "last_update": last_update,
        "cache_file": CACHE_FILE,
        "telegram_configured": bool(BOT_TOKEN and CHAT_ID)
    }

# Serving Production Frontend
if dist_path.exists():
    print(f"Frontend dist found at: {dist_path}")
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="static")

    @app.exception_handler(404)
    async def not_found_exception_handler(request, exc):
        # Serve index.html for all 404s to handle Vue Router history mode
        return FileResponse(dist_path / "index.html")
else:
    print(f"WARNING: Frontend dist NOT found at: {dist_path}")
    @app.get("/")
    async def root_fallback():
        return {
            "message": "Backend is running, but Frontend build (dist) is missing.",
            "path_searched": str(dist_path)
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
