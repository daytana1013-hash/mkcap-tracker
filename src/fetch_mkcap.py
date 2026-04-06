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
    # 최근 5 영업일 중 데이터 있는 날짜 자동 탐색
    today = datetime.now()
    for i in range(7):
        d = today - timedelta(days=i)
        if d.weekday() < 5:  # 평일만
            candidate = d.strftime("%Y%m%d")
            try:
                df = stock.get_market_cap(candidate, market="KOSPI")
                if len(df) > 0:
                    print(f"유효 기준일: {candidate}")
                    return candidate
            except:
                continue
    return (today - timedelta(days=3)).strftime("%Y%m%d")

def fetch_all(biz_date):
    results = {}
    for mkt in ["KOSPI", "KOSDAQ"]:
        try:
            cap_df   = stock.get_market_cap(biz_date, market=mkt)
            ohlcv_df = stock.get_market_ohlcv(biz_date, market=mkt)
            print(f"[{mkt}] cap컬럼={list(cap_df.columns)}")
            print(f"[{mkt}] ohlcv컬럼={list(ohlcv_df.columns)}")
            print(f"[{mkt}] cap행수={len(cap_df)}, ohlcv행수={len(ohlcv_df)}")

            for code in COVERAGE:
                if code not in cap_df.index: continue
                row_cap   = cap_df.loc[code]
                row_price = ohlcv_df.loc[code] if code in ohlcv_df.index else None

                # 시총: 첫번째 숫자 컬럼
                mkcap = 0
                for col in cap_df.columns:
                    try: mkcap = int(row_cap[col]) // 100000000; break
                    except: continue

                pri
