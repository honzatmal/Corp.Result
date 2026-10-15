import os
import requests
import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FMP_API_KEY = os.getenv("FMP_API_KEY")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def get_earnings_calendar():
    today = datetime.date.today()
    next_week = today + datetime.timedelta(days=7)
    
    # 최신 v3/earning-calendar (하이픈 형태) 또는 v4 엔드포인트로 변경
    url = f"https://financialmodelingprep.com/api/v3/earning-calendar?from={today}&to={next_week}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return f"⚠️ API 요청 실패 (상태 코드: {response.status_code})\n응답 내용: {response.text[:150]}"
    
    data = response.json()
    
    if isinstance(data, dict) and "Error Message" in data:
        return f"⚠️ FMP API 오류: {data['Error Message']}"
    
    if not isinstance(data, list):
        return f"⚠️ 데이터 형식 오류: {str(data)[:150]}"
    
    target_symbols = ["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "NFLX", "GOOGL", "META"]
    filtered_data = [item for item in data if item.get("symbol") in target_symbols]
    
    if not filtered_data:
        return f"📅 이번 주({today} ~ {next_week})에 예정된 주요 기업 실적 발표가 없습니다."
    
    message = "📊 **U.S. STOCK EARNINGS CALENDAR**\n\n"
    for item in filtered_data:
        symbol = item.get("symbol")
        date = item.get("date")
        eps_est = item.get("epsEstimated", "N/A")
        eps_act = item.get("eps", "N/A")
        
        status_emoji = "⚪"
        if eps_act != "N/A" and eps_est != "N/A":
            status_emoji = "🟢" if eps_act >= eps_est else "🔴"
            
        message += f"🔹 **{symbol}** ({date})\n"
        message += f"   - Est: `{eps_est}` | Act: `{eps_act}` {status_emoji}\n\n"
        
    return message

if __name__ == "__main__":
    report = get_earnings_calendar()
    send_telegram_message(report)
