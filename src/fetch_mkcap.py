import requests, json, os
from datetime import datetime, timedelta

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

API_KEY = os.environ.get("KRX_API_KEY","")

def get_biz_date():
    today = datetime.now()
    if today.weekday()==5: today -= timedelta(days=1)
    elif today.weekday()==6: today -= timedelta(days=2)
    return today.strftime("%Y%m%d")

def fetch_all(biz_date):
    results = {}
    headers = {"Referer":"https://open.krx.co.kr","User-Agent":"Mozilla/5.0"}
    for mktId, mkt_name in [("STK","KOSPI"),("KSQ","KOSDAQ")]:
        params = {
            "auth": API_KEY,
            "bld": "dbms/MDC/STAT/standard/MDCSTAT01501",
            "locale":"ko_KR","mktId":mktId,"trdDd":biz_date,
            "share":"1","money":"1","csvxls_isNo":"false",
        }
        try:
            r = requests.get(
                "https://open.krx.co.kr/contents/OPN/99/OPN99000001.jspx",
                params=params, headers=headers, timeout=15)
            for item in r.json().get("OutBlock_1",[]):
                code = item.get("ISU_SRT_CD","").strip()
                if code not in COVERAGE: continue
                mc = item.get("MKTCAP","0").replace(",","")
                pr = item.get("TDD_CLSPRC","0").replace(",","")
                ch = item.get("FLUC_RT","0").replace(",","")
                results[code] = {
                    "ticker":code,"name":COVERAGE[code],"market":mkt_name,
                    "price":int(pr) if pr.lstrip("-").isdigit() else 0,
                    "mkcap_eok":round(int(mc)/100) if mc.isdigit() else 0,
                    "chg_rate":float(ch) if ch.lstrip("-").replace(".","").isdigit() else 0.0,
                    "date":biz_date,
                }
            print(f"[{mkt_name}] {sum(1 for v in results.values() if v['market']==mkt_name)}개")
        except Exception as e:
            print(f"[ERROR] {mkt_name}: {e}")
    return results

def save(data, biz_date):
    os.makedirs("data", exist_ok=True)
    with open("data/latest.json","w",encoding="utf-8") as f:
        json.dump({"updated":biz_date,"stocks":list(data.values())},f,ensure_ascii=False,indent=2)
    hist = []
    if os.path.exists("data/history.json"):
        with open("data/history.json",encoding="utf-8") as f: hist = json.load(f)
    hist = [h for h in hist if h["date"]!=biz_date]
    hist.append({"date":biz_date,"stocks":list(data.values())})
    hist = sorted(hist,key=lambda x:x["date"],reverse=True)[:250]
    with open("data/history.json","w",encoding="utf-8") as f:
        json.dump(hist,f,ensure_ascii=False,indent=2)
    print(f"[DONE] {len(data)}개 저장")

if __name__=="__main__":
    if not API_KEY: print("[ERROR] KRX_API_KEY 없음"); exit(1)
    biz_date = get_biz_date()
    print(f"기준일: {biz_date}")
    data = fetch_all(biz_date)
    if data: save(data, biz_date)
    else: print("[ERROR] 데이터 없음"); exit(1)
