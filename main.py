import requests
import os

# إعداد المتغيرات من البيئة أو استبدلهم يدويًا بالقيم
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or "توكن_البوت"
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or "شات_ID"

# نص الرسالة الترحيبية
message = "👋 أهلاً بك! هذا اختبار لإرسال رسالة ترحيبية عبر البوت على Telegram."

# رابط API
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# إرسال الرسالة
response = requests.post(url, data={
    "chat_id": TELEGRAM_CHAT_ID,
    "text": message
})

# التحقق من النجاح
if response.status_code == 200:
    print("✅ تم إرسال الرسالة الترحيبية بنجاح!")
else:
    print("❌ فشل في إرسال الرسالة.")
    print(response.text)
