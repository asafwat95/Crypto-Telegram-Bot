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
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", {}).get("trades", [])
    else:
        print("Error fetching trades:", response.text)
        return []

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

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
    trades = get_trades()
    if not trades:
        print("No trades found.")
        return

    last_trade_id = load_last_trade_id()

    # الصفقات مرتبة من الأحدث للأقدم
    new_trades = []
    for trade in trades:
        if trade["id"] == last_trade_id:
            break
        new_trades.append(trade)

    if new_trades:
        # الأقدم أولاً
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
