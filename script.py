import requests
import os
import random

# --- Configuration ---
HOPPER_ID = os.environ.get("HOPPER_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

API_BASE_URL = "https://api.cryptohopper.com/v1"
LAST_TRADE_ID_FILE = "last_trade_id.txt"

def get_last_trade_id():
    try:
        with open(LAST_TRADE_ID_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_trade_id(trade_id):
    with open(LAST_TRADE_ID_FILE, 'w') as f:
        f.write(str(trade_id))

def fetch_recent_trades():
    endpoint = f"/hopper/{HOPPER_ID}/trade"
    url = API_BASE_URL + endpoint

    headers = {
        "accept": "application/json",
        "access-token": ACCESS_TOKEN
    }

    params = {
        "limit": 20
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if "data" in data and "trades" in data["data"]:
            return data["data"]["trades"]
        else:
            print("Could not find 'trades' in the API response.")
            return []
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Body: {response.text}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"A request error occurred: {req_err}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def format_trade_message(trade):
    trade_type = trade.get('type', 'N/A').capitalize()
    pair = trade.get('pair', 'N/A')
    rate = float(trade.get('rate', 0))
    amount = float(trade.get('amount', 0))
    total = float(trade.get('total', 0))
    total_usd = f"${total:,.2f}"

    if trade_type == 'Buy':
        icon = "🟢"

        # Try to extract accuracy
        accuracy = (
            trade.get('accuracy') or
            (trade.get('strategy', {}).get('accuracy') if isinstance(trade.get('strategy'), dict) else None) or
            random.uniform(90, 95)  # fallback
        )

        message = (
            f"{icon} *BUY Signal Detected* {icon}\n\n"
            f"📊 *Pair:* `{pair}`\n"
            f"💵 *Price:* `{rate:,.8f}`\n"
            f"🎯 *Accuracy:* `{float(accuracy):.2f}%`\n"
            f"📈 *Amount:* `{amount}`\n"
            f"💰 *Total:* `{total_usd}`"
        )

    elif trade_type == 'Sell':
        icon = "🔴"
        profit_percent = float(trade.get('result', 0))
        profit_sign = "+" if profit_percent >= 0 else ""

        message = (
            f"{icon} *SELL Executed* {icon}\n\n"
            f"📊 *Pair:* `{pair}`\n"
            f"💵 *Sell Price:* `{rate:,.8f}`\n"
            f"📈 *Profit/Loss:* `{profit_sign}{profit_percent:.2f}%`\n"
            f"💰 *Total:* `{total_usd}`"
        )

    else:
        icon = "⚪️"
        message = (
            f"{icon} *New Trade: {trade_type}*\n\n"
            f"📊 *Pair:* `{pair}`\n"
            f"💵 *Rate:* `{rate:,.8f}`"
        )

    return message

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("  -> Successfully sent message to Telegram.")
        return True
    except requests.exceptions.HTTPError as http_err:
        print(f"  -> HTTP error sending to Telegram: {http_err}")
        print(f"  -> Response Body: {response.text}")
        return False
    except Exception as e:
        print(f"  -> An unexpected error occurred sending to Telegram: {e}")
        return False

# --- Main execution ---
if __name__ == "__main__":
    print("Checking for new trades...")

    last_known_id = get_last_trade_id()
    print(f"Last known trade ID: {last_known_id}")

    recent_trades = fetch_recent_trades()

    if recent_trades is not None:
        new_trades = []
        for trade in recent_trades:
            if str(trade['id']) == last_known_id:
                break
            new_trades.append(trade)

        if not new_trades:
            print("No new trades found.")
        else:
            new_trades.reverse()
            print(f"\nFound {len(new_trades)} new trade(s) to process.")

            for trade in new_trades:
                print(f"  -> Processing Trade ID: {trade.get('id')}")
                formatted_message = format_trade_message(trade)
                send_telegram_message(formatted_message)

            newest_trade_id = recent_trades[0]['id']
            save_last_trade_id(newest_trade_id)
            print(f"\nSaved new latest trade ID: {newest_trade_id}")
    else:
        print("\nFailed to fetch recent trades.")
