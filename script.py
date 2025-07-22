import requests
import os
import json

# --- Configuration ---
HOPPER_ID = os.environ.get("HOPPER_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

API_BASE_URL = "https://api.cryptohopper.com/v1"
LAST_TRADE_FILE = "last_trade.json"

def get_trades():
    url = f"{API_BASE_URL}/hopper/{HOPPER_ID}/trades"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("data", {}).get("trades", [])
    except requests.exceptions.RequestException as e:
        error_message = f"❌ خطأ أثناء جلب البيانات من CryptoHopper:\n{str(e)}"
        send_telegram_message(error_message)
        return []

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"خطأ أثناء إرسال رسالة Telegram: {e}")

def load_last_trade_id():
    if os.path.exists(LAST_TRADE_FILE):
        with open(LAST_TRADE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_trade_id")
    return None

def save_last_trade_id(trade_id):
    with open(LAST_TRADE_FILE, "w") as f:
        json.dump({"last_trade_id": trade_id}, f)

def main():
    send_telegram_message("✅ اختبار: السكربت يعمل الآن بشكل طبيعي.")
    trades = get_trades()
    if not trades:
        print("No trades found.")
        return

    last_trade_id = load_last_trade_id()

    new_trades = []
    for trade in trades:
        if trade["id"] == last_trade_id:
            break
        new_trades.append(trade)

    if new_trades:
        for trade in reversed(new_trades):
            msg = f"💹 صفقة جديدة:\n\n"
            msg += f"🔸 العملة: {trade.get('currency')}\n"
            msg += f"🔁 النوع: {trade.get('type').capitalize()}\n"
            msg += f"💰 السعر: {trade.get('rate')}\n"
            msg += f"📦 الكمية: {trade.get('amount')}\n"
            msg += f"📅 التاريخ: {trade.get('datetime')}"
            send_telegram_message(msg)
        save_last_trade_id(new_trades[0]["id"])
    else:
        print("No new trades.")

if __name__ == "__main__":
    main()
