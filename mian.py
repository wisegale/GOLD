import time
import requests
from datetime import datetime, timezone

BASE_URL = "https://web3.okx.com/priapi/v1/nft/inscription/ordi-rc20/detail/items"
BASE_PARAMS = {
    "cursor": "MQ==",
    "orderType": "1",
    "pageSize": "20",
    "ticker": "₿؜",
    "tickerId": "",
    "tickerType": "0",
    "showPending": "false",
}

BOT_TOKEN = "8382432858:AAFnWca3Qm6C2agVve9mY5JZmOcUgGt8nq4"
CHAT_ID = "-4992112963"

CHECK_INTERVAL = 2  # 秒

def okx_server_ms():
    try:
        r = requests.get("https://www.okx.com/api/v5/public/time", timeout=5)
        r.raise_for_status()
        return int(r.json()["data"][0]["ts"])
    except Exception:
        return int(time.time() * 1000)

def get_floor_price():
    params = BASE_PARAMS.copy()
    params["t"] = okx_server_ms()
    headers = {
        "user-agent": "Mozilla/5.0",
        "referer": "https://www.okx.com/",
        "origin": "https://www.okx.com",
    }
    r = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    items = r.json()["data"]["items"]
    if not items:
        raise ValueError("接口返回 items 为空")
    return float(items[0]["floorPrice"])

def send_alert(price):
    text = f"金比特目前的价格是：{price},远低于地板价"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)

def main():
    last_price = None
    while True:
        try:
            price = get_floor_price()
            now_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{now_local} 目前的地板价是：{price}")
            if last_price is not None and (last_price - price) > -1:
                send_alert(price)
            last_price = price
        except Exception as exc:
            now_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{now_local} error: {exc}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

