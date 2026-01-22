@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║   نظام إدارة مخزون السيارات - تليجرام    ║
echo ║   Car Stock - Pure Telegram Cloud         ║
echo ╚════════════════════════════════════════════╝
echo.

cd backend

echo [1/3] فحص المكتبات...
pip install -r requirements.txt --quiet 2>nul

echo [2/3] فحص إعدادات التليجرام...
python -c "from dotenv import load_dotenv; import os; load_dotenv(); token=os.getenv('TELEGRAM_BOT_TOKEN',''); chat=os.getenv('TELEGRAM_CHAT_ID',''); exit(0 if (token and chat and len(token)>20) else 1)" 2>nul

if errorlevel 1 (
    echo.
    echo ⚠️  تحذير: التليجرام غير مُعد!
    echo.
    echo 📋 اتبع الخطوات في ملف: SETUP_TELEGRAM.md
    echo.
    echo 1. أنشئ بوت من @BotFather
    echo 2. أنشئ قناة خاصة
    echo 3. أضف البوت كـ Admin
    echo 4. احصل على Chat ID
    echo 5. حدّث ملف backend/.env
    echo.
    pause
)

echo [3/3] بدء الخادم...
echo.
echo ✅ API: http://localhost:8000
echo ✅ الموقع: افتح web-frontend/index.html
echo ✅ الاختبار: http://localhost:8000/health
echo.
echo 💡 للإيقاف: Ctrl+C
echo.

python main.py
