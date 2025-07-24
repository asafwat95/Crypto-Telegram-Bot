import requests
import os
import random
from datetime import datetime

# --- Configuration ---
HOPPER_ID = os.environ.get("HOPPER_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

API_BASE_URL = "https://api.cryptohopper.com/v1"
LAST_TRADE_ID_FILE = "last_trade_id.txt"
TRADE_LOG_FILE = "trades_log.txt"

def get_last_trade_id():
    try:
        with open(LAST_TRADE_ID_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_trade_id(trade_id):
    with open(LAST_TRADE_ID_FILE, 'w') as f:
        f.write(str(trade_id))

def log_trade(message):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        with open(TRADE_LOG_FILE, 'a') as f:
            f.write(f"--- {timestamp} ---\n")
            f.write(message + "\n\n")
        print("✅ Trade successfully logged to trades_log.txt")
    except Exception as e:
        print(f"❌ Failed to log trade: {e}")

def fetch_latest_trade():
    endpoint = f"/hopper/{HOPPER_ID}/trade"
    url = API_BASE_URL + endpoint

    headers = {
        "accept": "application/json",
        "access-token": ACCESS_TOKEN
    }

    params = {
        "limit": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if "data" in data and "trades" in data["data"] and len(data["data"]["trades"]) > 0:
            return data["data"]["trades"][0]
        else:
            print("No trades found in the response.")
            return None
    except requests.exceptions.RequestException as err:
        print(f"Error fetching trade: {err}")
        return None

def format_trade_message(trade):
    trade_type = trade.get('type', 'N/A').capitalize()
    pair = trade.get('pair', 'N/A')
    rate = float(trade.get('rate', 0))
    amount = float(trade.get('amount', 0))
    total = float(trade.get('total', 0))
    total_usd = f"${total:,.2f}"

    if trade_type == '
