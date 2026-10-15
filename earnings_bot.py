import os
import datetime
import requests
import pandas as pd
import yfinance as yf

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

NASDAQ_TOP_20 = {
    "AAPL": "애플", "MSFT": "마이크로소프트", "NVDA": "엔비디아", "GOOGL": "알파벳(구글)",
    "AMZN": "아마존", "META": "메타", "TSLA": "테슬라", "AVGO": "브로드컴",
    "COST": "코스트코", "NFLX": "넷플릭스", "AMD": "AMD", "TMUS": "T모바일",
    "ADBE": "어도비", "CSCO": "시스코 시스템즈", "INTC": "인텔", "QCOM": "퀄컴",
    "AMGN": "암젠", "TXN": "텍사스 인스트루먼트", "HON": "허니웰", "SBUX": "스타벅스"
}

SP500_TOP_20 = {
    "BRK-B": "버크셔 해서웨이", "JPM": "JP모건 체이스", "V": "비자", "WMT": "월마트",
    "MA": "마스터카드", "UNH": "유나이티드헬스", "PG": "P&G", "HD": "홈디포",
    "BAC": "뱅크오브아메리카", "CVX": "셰브론", "LLY": "일라이 릴리", "ABBV": "애브비",
    "MRK": "머크", "KO": "코카콜라", "PEP": "펩시코", "ACN": "액센츄어",
    "MCD": "맥도날드", "LIN": "린데", "PM": "필립 모리스", "TMO": "써모 피셔 사이언티픽"
}

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print(f"Telegram Response: {response.status_code}, {response.text}")

def check_earnings(group_name, symbol_dict):
    today = datetime.date.today()
    year_month_str = today.strftime('%Y년 %m월')
    date_prefix = today.strftime('%Y-%m')
    
    # 1. 매월 1일인 경우: 월간 일정표 (카드 스타일 UI)
    if True:
        message = f"📌 *[{year_month_str}] {group_name} 실적 캘린더*\n"
        message += "━━━━━━━━━━━━━━━━━━━\n"
        found = False
        
        for symbol, kr_name in symbol_dict.items():
            try:
                ticker = yf.Ticker(symbol)
                cal = ticker.calendar
                if cal is not None and not cal.empty and "Earnings Date" in cal:
                    dates = cal["Earnings Date"]
                    if len(dates) > 0:
                        edate = str(dates.iloc[0]).split(" ")[0]
                        if edate.startswith(date_prefix):
                            found = True
                            message += f"▪️ *{kr_name}* (`{symbol}`)\n"
                            message += f"  └ 일정 : `{edate}`\n"
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue
                
        if not found:
            message += "_이번 달 등록된 실적 발표 일정이 없습니다._\n"
            
        message += "━━━━━━━━━━━━━━━━━━━"
        send_telegram_message(message)
        return

    # 2. 평상시(매일 실행): 당일 실적 발표 알림 (카드 스타일 UI)
    today_str = today.strftime('%Y-%m-%d')
    message = f"🔔 *[{today_str}] {group_name} 실적 발표 D-DAY*\n"
    message += "━━━━━━━━━━━━━━━━━━━\n"
    announced_any = False

    for symbol, kr_name in symbol_dict.items():
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
                            
                        message += f"🚀 *{kr_name}* (`{symbol}`)\n"
                        message += f"  └ 예상 EPS (Est) : `{eps_est}`\n\n"
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            continue

    if announced_any:
        message += "━━━━━━━━━━━━━━━━━━━"
        send_telegram_message(message)

def job():
    check_earnings("나스닥 Top 20", NASDAQ_TOP_20)
    check_earnings("S&P 500 Top 20", SP500_TOP_20)

if __name__ == "__main__":
    job()
