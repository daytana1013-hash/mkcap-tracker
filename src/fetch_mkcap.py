import json, os
from datetime import datetime, timedelta
from pykrx import stock

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

def get_biz_date():
    today = datetime.now()
    if today.weekday() == 5: today -= timedelta(days=1)
    elif today.weekday() == 6: today -= timedelta(days=2)
    return today.strftime("%Y%m%d")

def fetch_all(biz_date):
    results = {}
    for mkt in ["KOSPI", "KOSDAQ"]:
        try:
            # 시가총액
            cap_df = stock.get_market_cap(biz_date, market=mkt)
            print(f"[{mkt}] cap 컬럼: {list(cap_df.columns)}")

            # 주가
            ohlcv_df = stock.get_market_ohlcv(biz_date, market=mkt)
            print(f"[{mkt}] ohlcv 컬럼: {list(ohlcv_df.columns)}")

            # 컬럼 자동 감지
            cap_col = [c for c in cap_df.columns if '시가총액' in c or 'cap' in c.lower() or 'Mktcap' in c]
            close_col = [c for c in ohlcv_df.columns if '종가' in c or c == 'Close' or c == 'close']
            chg_col = [c for c in ohlcv_df.columns if '등락' in c or c == 'Change' or c == 'Chg' or '변동' in c]

            cap_key   = cap_col[0]   if cap_col   else list(cap_df.columns)[0]
            close_key = close_col[0] if close_col else list(ohlcv_df.columns)[3]
            chg_key   = chg_col[0]   if chg_col   else None

            print(f"[{mkt}] 사용 컬럼 → 시총:{cap_key}, 종가:{close_key}, 등락:{chg_key}")

            for code in COVERAGE:
                if code not in cap_df.index: continue
                mkcap = int(cap_df.loc[code, cap_key]) // 100000000
                price = int(ohlcv_df.loc[code, close_key]) if code in ohlcv_df.index else 0
                chg   = float(ohlcv_df.loc[code, chg_key]) if (chg_key and code in ohlcv_df.index) else 0.0
                results[code] = {
                    "ticker": code, "name": COVERAGE[code], "market": mkt,
                    "price": price, "mkcap_eok": mkcap,
                    "chg_rate": round(chg, 2), "date": biz_date,
                }
            print(f"[{mkt}] {sum(1 for v in results.values() if v['market']==mkt)}개 매칭")
        except Exception as e:
            print(f"[ERROR] {mkt}: {e}")
    return results

def save(data, biz_date):
    os.makedirs("data", exist_ok=True)
    with open("data/latest.json", "w", encoding="utf-8") as f:
        json.dump({"updated": biz_date, "stocks": list(data.values())}, f, ensure_ascii=False, indent=2)
    hist = []
    if os.path.exists("data/history.json"):
        with open("data/history.json", encoding="utf-8") as f: hist = json.load(f)
    hist = [h for h in hist if h["date"] != biz_date]
    hist.append({"date": biz_date, "stocks": list(data.values())})
    hist = sorted(hist, key=lambda x: x["date"], reverse=True)[:250]
    with open("data/history.json", "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)
    print(f"[DONE] {len(data)}개 저장")

if __name__ == "__main__":
    biz_date = get_biz_date()
    print(f"기준일: {biz_date}")
    data = fetch_all(biz_date)
    if data: save(data, biz_date)
    else: print("[ERROR] 데이터 없음"); exit(1)
