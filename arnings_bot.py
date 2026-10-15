import os
import requests
import datetime

# 환경 변수 또는 직접 입력
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
FMP_API_KEY = os.getenv("FMP_API_KEY", "YOUR_FMP_API_KEY")

def get_earnings_calendar():
    # 오늘 기준 이번 주/이번 달 실적 발표 일정 조회
    today = datetime.date.today()
    next_week = today + datetime.timedelta(days=7)
    
    url = f"https://financialmodelingprep.com/api/v3/earning_calendar?from={today}&to={next_week}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return "⚠️ 실적 데이터를 가져오는데 실패했습니다."
    
    data = response.json()
    
    # 관심 종목 리스트
    target_symbols = ["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "NFLX", "GOOGL", "META"]
    filtered_data = [item for item in data if item.get("symbol") in target_symbols]
    
    if not filtered_data:
        return "📅 이번 주에 예정된 주요 기업 실적 발표가 없습니다."
    
    message = "📊 **U.S. STOCK EARNINGS CALENDAR**\n\n"
    for item in filtered_data:
        symbol = item.get("symbol")
        date = item.get("date")
        eps_est = item.get("epsEstimated", "N/A")
        eps_act = item.get("eps", "N/A")
        
        # 실적 결과에 따른 이모지 표시 (어닝 서프라이즈: 🟢, 쇼크: 🔴)
        status_emoji = "⚪"
        if eps_act != "N/A" and eps_est != "N/A":
            status_emoji = "🟢" if eps_act >= eps_est else "🔴"
            
        message += f"🔹 **{symbol}** ({date})\n"
        message += f"   - Est: `{eps_est}` | Act: `{eps_act}` {status_emoji}\n\n"
        
    return message

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    report = get_earnings_calendar()
    send_telegram_message(report)
