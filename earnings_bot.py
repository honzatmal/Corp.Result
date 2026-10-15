import os
import datetime
import requests
import yfinance as yf

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def get_earnings_calendar():
    target_symbols = ["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "NFLX", "GOOGL", "META"]
    
    message = "📊 **U.S. STOCK EARNINGS CALENDAR**\n\n"
    found = False

    for symbol in target_symbols:
        try:
            ticker = yf.Ticker(symbol)
            # 야후 파이낸스에서 실적 발표 일정 가져오기
            calendar = ticker.calendar
            
            if calendar is not None and not calendar.empty:
                found = True
                # 날짜 및 예상치 추출
                earnings_date = "확인 중"
                if "Earnings Date" in calendar:
                    dates = calendar["Earnings Date"]
                    if len(dates) > 0:
                        earnings_date = str(dates.iloc[0]).split(" ")[0]
                
                eps_est = calendar.get("Earnings High", "N/A")
                if isinstance(eps_est, pd.Series) and not eps_est.empty:
                    eps_est = eps_est.iloc[0]

                message += f"🔹 **{symbol}**\n"
                message += f"   - 발표 예정일: `{earnings_date}`\n"
                message += f"   - 예상 EPS (Est): `{eps_est}`\n\n"
        except Exception as e:
            # 개별 종목 조회 실패 시 건너뜀
            continue

    if not found:
        # 야후 파이낸스 캘린더 데이터가 비어있을 경우를 대비한 안내
        return "📅 현재 조회된 주요 기업의 다가오는 실적 발표 일정이 없습니다."
        
    return message

if __name__ == "__main__":
    report = get_earnings_calendar()
    send_telegram_message(report)
