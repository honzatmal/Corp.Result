import os
import datetime
import requests
import pandas as pd
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
    response = requests.post(url, json=payload)
    print(f"Telegram Response: {response.status_code}, {response.text}")

def job():
    today = datetime.date.today()
    target_symbols = ["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "NFLX", "GOOGL", "META"]
    
    # 1. 매월 1일인 경우: 이번 달 전체 실적 일정 안내
    if True:
        message = f"🗓️ **[{today.strftime('%Y년 %m월')}] 주요 기업 실적 발표 월간 일정표**\n\n"
        found = False
        
        for symbol in target_symbols:
            try:
                ticker = yf.Ticker(symbol)
                cal = ticker.calendar
                if cal is not None and not cal.empty and "Earnings Date" in cal:
                    dates = cal["Earnings Date"]
                    if len(dates) > 0:
                        edate = str(dates.iloc[0]).split(" ")[0]
                        if edate.startswith(today.strftime('%Y-%m')):
                            found = True
                            message += f"🔹 **{symbol}**: `{edate}`\n"
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue
                
        if not found:
            message += "이번 달 실적 발표 없음"
            
        send_telegram_message(message)
        return

    # 2. 평상시(매일 실행): 오늘 실적 발표가 있는 기업 체크 및 결과 전송
    today_str = today.strftime('%Y-%m-%d')
    message = f"📊 **[{today_str}] 오늘의 실적 발표 알림**\n\n"
    announced_any = False

    for symbol in target_symbols:
        try:
            ticker = yf.Ticker(symbol)
            cal = ticker.calendar
            if cal is not None and not cal.empty and "Earnings Date" in cal:
                dates = cal["Earnings Date"]
                if len(dates) > 0:
                    edate = str(dates.iloc[0]).split(" ")[0]
                    if edate == today_str:
                        announced_any = True
                        eps_est = cal.get("Earnings High", "N/A")
                        if isinstance(eps_est, pd.Series) and not eps_est.empty:
                            eps_est = eps_est.iloc[0]
                            
                        message += f"📢 **{symbol} 실적 발표일입니다!**\n"
                        message += f"   - 예상 EPS (Est): `{eps_est}`\n\n"
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            continue

    if announced_any:
        send_telegram_message(message)
    else:
        print(f"[{today_str}] 오늘 발표 예정인 기업이 없습니다.")

if __name__ == "__main__":
    job()
