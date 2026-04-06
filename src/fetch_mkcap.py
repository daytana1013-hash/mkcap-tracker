"""
야후 파이낸스 기반 시가총액 수집기
- 15분 지연 실시간 시세
- API 키 불필요
"""

import json, os, time
import requests
from datetime import datetime

COVERAGE = {
    "005930":"삼성전자","066570":"LG전자","034220":"LG디스플레이",
    "213420":"덕산네오룩스","009150":"삼성전기","011070":"LG이노텍",
    "353200":"대덕전자","097520":"이수페타시스","222800":"심텍",
    "356860":"티엘비","007810":"코리아써키트","064760":"티씨케이",
    "195870":"해성디에스","090460":"비에이치","272290":"이녹스첨단소재",
    "051370":"인터플렉스","000150":"두산","020150":"롯데에너지머티리얼즈",
    "336370":"솔루스첨단소재","120110":"코오롱인더","077360":"덕산하이메탈",
    "301880":"네오티스","039030":"이오테크닉스","066900":"디에이피",
}

MARKET_MAP = {
    "005930":"KS","066570":"KS","034220":"KS","009150":"KS","011070":"KS",
    "353200":"KS","007810":"KS","195870":"KS","000150":"KS","020150":"KS",
    "336370":"KS","120110":"KS",
    "213420":"KQ","097520":"KQ","222800":"KQ","356860":"KQ","064760":"KQ",
    "090460":"KQ","272290":"KQ","051370":"KQ","077360":"KQ","301880":"KQ",
    "039030":"KQ","066900":"KQ",
}

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch_yahoo(code):
    suffix = MARKET_MAP.get(code, "KS")
    ticker = f"{code}.{suffix}"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    try:
        r = requests.get(url, headers=HEADERS, params={"interval":"1d","range":"1d"}, timeout=10)
        meta = r.json()["chart"]["result"][0]["meta"]
        price  = meta.get("regularMarketPrice", 0)
        prev   = meta.get("previousClose", price)
        shares = meta.get("sharesOutstanding", 0)
        chg    = round((price - prev) / prev * 100, 2) if prev else 0.0
        mkcap  = int(shares * price) // 100000000 if shares and price else 0
        return {
            "ticker": code, "name": COVERAGE[code],
            "market": "KOSPI" if suffix=="KS" else "KOSDAQ",
            "price": int(price), "mkcap_eok": mkcap,
            "chg_rate": chg, "date": datetime.now().strftime("%Y%m%d"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception as e:
        print(f"  [{code}] 오류: {e}")
        return None

def fetch_all():
    results = {}
    for i, (code, name) in enumerate(COVERAGE.items(), 1):
        print(f"[{i}/{len(COVERAGE)}] {name} 조회 중...")
        r = fetch_yahoo(code)
        if r:
            results[code] = r
            print(f"  → {r['price']:,}원 / {r['mkcap_eok']:,}억 / {r['chg_rate']:+.2f}%")
        time.sleep(0.3)
    return results

def save(data):
    os.makedirs("data", exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    with open("data/latest.json","w",encoding="utf-8") as f:
        json.dump({"updated":today,"updated_at":datetime.now().strftime("%Y-%m-%d %H:%M"),
                   "source":"Yahoo Finance (15분 지연)","stocks":list(data.values())},
                  f, ensure_ascii=False, indent=2)
    hist = []
    if os.path.exists("data/history.json"):
        with open("data/history.json",encoding="utf-8") as f: hist = json.load(f)
    hist = [h for h in hist if h["date"]!=today]
    hist.append({"date":today,"stocks":list(data.values())})
    hist = sorted(hist,key=lambda x:x["date"],reverse=True)[:250]
    with open("data/history.json","w",encoding="utf-8") as f:
        json.dump(hist,f,ensure_ascii=False,indent=2)
    print(f"[DONE] {len(data)}개 저장")

if __name__=="__main__":
    data = fetch_all()
    if data: save(data)
    else: print("[ERROR] 데이터 없음"); exit(1)
