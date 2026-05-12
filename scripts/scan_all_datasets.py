#!/usr/bin/env python3
"""Scan Twinkle Hub for ALL datasets relevant to Bizmap expansion."""
import subprocess, json, time

API = "https://api.twinkleai.tw/mcp/"
KEY = "***REMOVED***"

def mc(m, p, t=60):
    pld = json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p})
    r = subprocess.run(["curl","-s","--max-time","60","-X","POST",API,
        "-H","Content-Type: application/json","-H","Accept: application/json, text/event-stream",
        "-H",f"Authorization: Bearer {KEY}","-d",pld],capture_output=True,text=True,timeout=t+30)
    d = r.stdout
    if "data: " in d: d = d.split("data: ",1)[1].strip()
    return json.loads(d)

# Explore all domains for biz-relevant datasets
explore = [
    # New category candidates
    ("停車場", "transport"),
    ("加油站", "utilities_telecom"),
    ("銀行", "economy_business"),
    ("寺廟", "culture_tourism_sport"),
    ("景點", "culture_tourism_sport"),
    ("寵物", "agriculture_fisheries"),
    ("長照", "health_food"),
    ("動物醫院", "agriculture_fisheries"),
    ("藥商", "health_food"),
    ("醫事檢驗所", "health_food"),
    ("物理治療所", "health_food"),
    ("不動產經紀", "economy_business"),
    ("會計", "economy_business"),
    ("法律", "economy_business"),
    ("旅館", "culture_tourism_sport"),
    ("觀光", "culture_tourism_sport"),
    
    # Expand existing categories
    ("食品業者", "health_food"),
    ("量販店", "economy_business"),
    ("超級市場", "economy_business"),
    ("補習班", "education_research"),
    ("健身", "culture_tourism_sport"),
    ("保全", "economy_business"),
    ("殯葬", "economy_business"),
    ("醫事機構", "health_food"),
    ("眼鏡", "health_food"),
    ("中醫", "health_food"),
    ("牙醫", "health_food"),
    ("水產", "agriculture_fisheries"),
    ("農產品", "agriculture_fisheries"),
    ("租賃", "economy_business"),
    ("托嬰", "health_food"),
    ("幼兒園", "education_research"),
    ("計程車", "transport"),
]

results = []
for q, dom in explore:
    try:
        res = mc("tools/call", {
            "name": "opendata-search_datasets",
            "arguments": {"query": q, "domain": dom, "limit": 3}
        }, t=30)
        txt = res["result"]["content"][0]["text"]
        data = json.loads(txt)
        hits = data.get("hits", [])
        for h in hits:
            n = h.get("name","")
            agency = h.get("agency","")
            norm = h.get("is_normalised", False)
            qual = h.get("quality_tier","")
            dsid = h["dataset_id"]
            results.append((q, dom, dsid, n[:55], agency[:20], qual, norm))
    except:
        pass
    time.sleep(0.2)

# Group by search query
print(f"{'Query':16s} {'Domain':24s} {'DatasetID':8s} {'Name':55s} {'Agency':20s} {'Qual':5s} {'Norm':5s}")
print("="*140)
for q, dom, dsid, name, agency, qual, norm in results:
    print(f"{q:16s} {dom:24s} {dsid:8s} {name:55s} {agency:20s} {qual:5s} {str(norm):5s}")
