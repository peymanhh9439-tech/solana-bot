import requests
import os

# ----------------------------
# 🌐 تابع اصلی برای دریافت توکن‌ها از چند API
# ----------------------------
def get_new_tokens():
    # لیست APIها — اولویت اول CoinGecko، بعد DexScreener، بعد Birdeye
    apis = [
        fetch_from_coingecko,
        fetch_from_dexscreener,
        fetch_from_birdeye
    ]
    
    for api_func in apis:
        print(f"🔄 Trying {api_func.__name__}...")
        tokens = api_func()
        if tokens:  # اگر داده معتبر گرفتیم
            print(f"✅ Success with {api_func.__name__}!")
            return tokens
        else:
            print(f"❌ {api_func.__name__} failed. Trying next...")
    
    print("🚨 All APIs failed. No data available.")
    return []

# ----------------------------
# 🌐 دریافت از CoinGecko
# ----------------------------
def fetch_from_coingecko():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        filtered_tokens = []
        for item in data:
            # فقط توکن‌هایی که روی Solana هستند — با بررسی شبکه (platforms)
            platforms = item.get("platforms", {})
            if "solana" in platforms:
                market_cap = item.get("market_cap", 0)
                if market_cap and market_cap < 1000000:  # زیر 1M
                    token_info = {
                        "source": "CoinGecko",
                        "symbol": item.get("symbol", "N/A").upper(),
                        "name": item.get("name", "N/A"),
                        "price": item.get("current_price", "N/A"),
                        "market_cap": market_cap,
                        "volume_24h": item.get("total_volume", "N/A"),
                        "change_24h": item.get("price_change_percentage_24h", "N/A")
                    }
                    filtered_tokens.append(token_info)
        
        return filtered_tokens
    except Exception as e:
        return None  # اگر خطا داد، None برگردون

# ----------------------------
# 🌐 دریافت از DexScreener
# ----------------------------
def fetch_from_dexscreener():
    url = "https://api.dexscreener.com/latest/dex/tokens"
    params = {
        "chain": "Solana",
        "limit": 50
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        filtered_tokens = []
        for item in data:
            market_cap = item.get("marketCap", 0)
            if market_cap and market_cap < 1000000:
                token_info = {
                    "source": "DexScreener",
                    "symbol": item.get("symbol", "N/A"),
                    "contract": item.get("address", "N/A"),
                    "price": item.get("price", "N/A"),
                    "market_cap": market_cap,
                    "volume_24h": item.get("volume", "N/A"),
                    "created_at": item.get("createdAt", "N/A")
                }
                filtered_tokens.append(token_info)
        
        return filtered_tokens
    except Exception:
        return None

# ----------------------------
# 🌐 دریافت از Birdeye (اگر API Key داری)
# ----------------------------
def fetch_from_birdeye():
    api_key = os.getenv("BIRDEYE_API_KEY")
    if not api_key:
        return None
    
    url = "https://api.birdeye.so/v1/tokenlist"
    headers = {"X-API-Key": api_key}
    params = {
        "chain": "solana",
        "sort_by": "market_cap",
        "order": "desc",
        "limit": 50
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json().get("data", [])
        
        filtered_tokens = []
        for item in data:
            market_cap = item.get("marketCap", 0)
            if market_cap and market_cap < 1000000:
                token_info = {
                    "source": "Birdeye",
                    "symbol": item.get("symbol", "N/A"),
                    "contract": item.get("address", "N/A"),
                    "price": item.get("price", "N/A"),
                    "market_cap": market_cap,
                    "volume_24h": item.get("volume24h", "N/A")
                }
                filtered_tokens.append(token_info)
        
        return filtered_tokens
    except Exception:
        return None

# ----------------------------
# 📊 نمایش اطلاعات توکن‌ها
# ----------------------------
def display_tokens(tokens):
    print("\n📋 New Solana Memecoins Found:")
    print("-" * 60)
    for token in tokens:
        source = token.get("source", "N/A")
        symbol = token.get("symbol", "N/A")
        name = token.get("name", "N/A")
        contract = token.get("contract", "N/A")
        price = token.get("price", "N/A")
        market_cap = token.get("market_cap", "N/A")
        volume = token.get("volume_24h", "N/A")
        change = token.get("change_24h", "N/A")
        
        print(f"🌐 Source: {source}")
        print(f"📌 Symbol: {symbol}")
        if name != "N/A": 
            print(f"📛 Name: {name}")
        if contract != "N/A": 
            print(f"🔗 Contract: {contract}")
        print(f"💰 Price: ${price:.8f}" if isinstance(price, (int, float)) else f"💰 Price: {price}")
        print(f"📊 Market Cap: ${market_cap:,}")
        print(f"📈 24h Volume: ${volume:,}" if isinstance(volume, (int, float)) else f"📈 24h Volume: {volume}")
        if change != "N/A":
            print(f"📈 24h Change: {change:+.2f}%")
        print("-" * 60)

# ----------------------------
# 🚀 اجرای اصلی
# ----------------------------
def main():
    print("🔍 Scanning Solana network for new memecoins...")
    tokens = get_new_tokens()
    
    if tokens:
        display_tokens(tokens)
    else:
        print("🚫 No new tokens found from any API.")

# ----------------------------
# 🔁 اجرا
# ----------------------------
if __name__ == "__main__":
    main()